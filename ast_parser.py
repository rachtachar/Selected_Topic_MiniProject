"""
Code Graph Builder using AST and Kuzu Database.
Extracts Modules, Functions, Classes, and relationships (CALLS, IMPORTS, DEFINED_IN).
"""
import ast
import os
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
import kuzu


class CodeGraphBuilder:
    """
    Parses Python source code AST and stores code structure into Kuzu Graph Database.
    """

    def __init__(self, db_path: str = "graph_db", clear_existing: bool = False):
        self.db_path = db_path
        if clear_existing and Path(db_path).exists():
            if Path(db_path).is_dir():
                shutil.rmtree(db_path, ignore_errors=True)
            else:
                try:
                    Path(db_path).unlink()
                except Exception:
                    pass


        self.db = kuzu.Database(db_path)
        self.conn = kuzu.Connection(self.db)
        self._init_schema()

    def _init_schema(self) -> None:
        """Create graph node and relationship tables if they don't exist."""
        # 1. Node tables
        self.conn.execute(
            "CREATE NODE TABLE IF NOT EXISTS Function ("
            "    name STRING, "
            "    file STRING, "
            "    line INT64, "
            "    PRIMARY KEY (name)"
            ")"
        )
        self.conn.execute(
            "CREATE NODE TABLE IF NOT EXISTS Class ("
            "    name STRING, "
            "    file STRING, "
            "    line INT64, "
            "    PRIMARY KEY (name)"
            ")"
        )
        self.conn.execute(
            "CREATE NODE TABLE IF NOT EXISTS Module ("
            "    name STRING, "
            "    filepath STRING, "
            "    PRIMARY KEY (name)"
            ")"
        )

        # 2. Relationship tables
        self.conn.execute("CREATE REL TABLE IF NOT EXISTS CALLS (FROM Function TO Function)")
        self.conn.execute("CREATE REL TABLE IF NOT EXISTS DEFINED_IN (FROM Function TO Module)")
        self.conn.execute("CREATE REL TABLE IF NOT EXISTS CLASS_DEFINED_IN (FROM Class TO Module)")
        self.conn.execute("CREATE REL TABLE IF NOT EXISTS IMPORTS (FROM Module TO Module)")

    def parse_file(self, filepath: str) -> bool:
        """
        Parse single Python file and extract AST nodes and relationships.
        """
        path = Path(filepath)
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source)
        except Exception as e:
            print(f"  [ast_parser] Warning parsing {filepath}: {e}")
            return False

        module_name = path.stem
        # Register module node
        self.conn.execute(
            "MERGE (m:Module {name: $name}) ON CREATE SET m.filepath = $filepath",
            {"name": module_name, "filepath": str(path.as_posix())}
        )

        # 1. Imports extraction
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_mod = alias.name.split(".")[-1]
                    self.conn.execute("MERGE (dep:Module {name: $n}) ON CREATE SET dep.filepath = ''", {"n": imported_mod})
                    self.conn.execute(
                        "MATCH (m:Module {name: $m}), (dep:Module {name: $d}) MERGE (m)-[:IMPORTS]->(dep)",
                        {"m": module_name, "d": imported_mod}
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported_mod = node.module.split(".")[-1]
                    self.conn.execute("MERGE (dep:Module {name: $n}) ON CREATE SET dep.filepath = ''", {"n": imported_mod})
                    self.conn.execute(
                        "MATCH (m:Module {name: $m}), (dep:Module {name: $d}) MERGE (m)-[:IMPORTS]->(dep)",
                        {"m": module_name, "d": imported_mod}
                    )

        # 2. Classes extraction
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                cls_key = f"{module_name}.{node.name}"
                self.conn.execute(
                    "MERGE (c:Class {name: $name}) ON CREATE SET c.file = $file, c.line = $line",
                    {"name": cls_key, "file": str(path.as_posix()), "line": node.lineno}
                )
                self.conn.execute(
                    "MATCH (c:Class {name: $c}), (m:Module {name: $m}) MERGE (c)-[:CLASS_DEFINED_IN]->(m)",
                    {"c": cls_key, "m": module_name}
                )

        # 3. Functions extraction and Calls
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_key = f"{module_name}.{node.name}"
                self.conn.execute(
                    "MERGE (f:Function {name: $name}) ON CREATE SET f.file = $file, f.line = $line",
                    {"name": func_key, "file": str(path.as_posix()), "line": node.lineno}
                )
                self.conn.execute(
                    "MATCH (f:Function {name: $fn}), (m:Module {name: $mn}) MERGE (f)-[:DEFINED_IN]->(m)",
                    {"fn": func_key, "mn": module_name}
                )

                # Scan function body for function calls
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        callee_name = None
                        if isinstance(child.func, ast.Name):
                            callee_name = child.func.id
                        elif isinstance(child.func, ast.Attribute):
                            callee_name = child.func.attr
                        
                        if callee_name:
                            # Register callee target if not exists
                            self.conn.execute(
                                "MERGE (b:Function {name: $name}) ON CREATE SET b.file = '', b.line = 0",
                                {"name": callee_name}
                            )
                            # Create CALLS relation
                            self.conn.execute(
                                "MATCH (a:Function {name: $src}), (b:Function {name: $dst}) "
                                "MERGE (a)-[:CALLS]->(b)",
                                {"src": func_key, "dst": callee_name}
                            )
        return True

    def parse_directory(self, directory_path: str, skip_dirs: Optional[set] = None) -> int:
        """Scan directory and parse all Python files."""
        if skip_dirs is None:
            skip_dirs = {".venv", "__pycache__", ".git", ".idea", "node_modules", "dist", "build"}

        count = 0
        for root, dirs, files in os.walk(directory_path):
            dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith(".")]
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    if self.parse_file(full_path):
                        count += 1
        return count

    def get_summary(self) -> Dict[str, int]:
        """Return counts of nodes and relationships in the graph."""
        try:
            f_res = self.conn.execute("MATCH (f:Function) WHERE f.file <> '' RETURN count(f) AS c").get_as_df()
            f_count = int(f_res["c"][0]) if not f_res.empty else 0

            m_res = self.conn.execute("MATCH (m:Module) WHERE m.filepath <> '' RETURN count(m) AS c").get_as_df()
            m_count = int(m_res["c"][0]) if not m_res.empty else 0

            c_res = self.conn.execute("MATCH (c:Class) RETURN count(c) AS c").get_as_df()
            c_count = int(c_res["c"][0]) if not c_res.empty else 0

            call_res = self.conn.execute("MATCH ()-[r:CALLS]->() RETURN count(r) AS c").get_as_df()
            call_count = int(call_res["c"][0]) if not call_res.empty else 0

            imp_res = self.conn.execute("MATCH ()-[r:IMPORTS]->() RETURN count(r) AS c").get_as_df()
            imp_count = int(imp_res["c"][0]) if not imp_res.empty else 0

            return {
                "functions": f_count,
                "modules": m_count,
                "classes": c_count,
                "calls": call_count,
                "imports": imp_count,
            }
        except Exception:
            return {"functions": 0, "modules": 0, "classes": 0, "calls": 0, "imports": 0}
