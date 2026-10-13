#!/usr/bin/env python3
"""
Apache Superset 数据连接器
支持 30+ 数据库连接管理、Schema 发现、数据集创建

天龙引擎 V8.41 集成
"""

import os
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 导入认证管理器
try:
    from superset_auth import SupersetAuth
except ImportError:
    pass


@dataclass
class DatabaseInfo:
    """数据库信息"""
    id: int
    name: str
    backend: str
    sqlalchemy_uri: str
    expose_in_sqllab: bool = True
    allow_run_async: bool = False
    allow_csv_upload: bool = True


@dataclass
class DatasetInfo:
    """数据集信息"""
    id: int
    database_id: int
    table_name: str
    schema: Optional[str] = None
    columns: List[Dict[str, Any]] = field(default_factory=list)


class DatabaseManager:
    """Superset 数据库管理器"""

    def __init__(self, auth: "SupersetAuth" = None, base_url: str = None):
        """初始化数据库管理器

        Args:
            auth: SupersetAuth 认证实例
            base_url: Superset URL（如果未提供 auth）
        """
        if auth:
            self.auth = auth
            self.base_url = auth.config.base_url
        else:
            self.base_url = base_url or os.getenv("SUPERSET_BASE_URL")
            self.auth = None

        # 移除 URL 末尾斜杠
        self.base_url = self.base_url.rstrip("/") if self.base_url else None

        # 初始化 HTTP 会话
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """创建 HTTP 会话"""
        session = requests.Session()

        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        if self.auth:
            return self.auth.get_headers()
        return {"Content-Type": "application/json"}

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送 API 请求

        Args:
            method: HTTP 方法
            endpoint: API 端点
            **kwargs: 请求参数

        Returns:
            响应数据
        """
        url = f"{self.base_url}/api/v1/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        headers.update(kwargs.pop("headers", {}))

        response = self.session.request(
            method,
            url,
            headers=headers,
            timeout=kwargs.pop("timeout", 30),
            **kwargs
        )
        response.raise_for_status()

        return response.json()

    # ==================== 数据库管理 ====================

    def list_databases(self) -> List[DatabaseInfo]:
        """列出所有数据库

        Returns:
            数据库信息列表
        """
        result = self._request("GET", "database/")
        databases = []

        for item in result.get("result", []):
            databases.append(DatabaseInfo(
                id=item["id"],
                name=item["database_name"],
                backend=item.get("backend", "unknown"),
                sqlalchemy_uri=item.get("sqlalchemy_uri", ""),
                expose_in_sqllab=item.get("expose_in_sqllab", True),
                allow_run_async=item.get("allow_run_async", False),
                allow_csv_upload=item.get("allow_csv_upload", True)
            ))

        return databases

    def get_database(self, database_id: int) -> DatabaseInfo:
        """获取数据库详情

        Args:
            database_id: 数据库 ID

        Returns:
            数据库信息
        """
        result = self._request("GET", f"database/{database_id}")
        item = result.get("result", {})

        return DatabaseInfo(
            id=item["id"],
            name=item["database_name"],
            backend=item.get("backend", "unknown"),
            sqlalchemy_uri=item.get("sqlalchemy_uri", ""),
            expose_in_sqllab=item.get("expose_in_sqllab", True),
            allow_run_async=item.get("allow_run_async", False),
            allow_csv_upload=item.get("allow_csv_upload", True)
        )

    def create_database(
        self,
        database_name: str,
        sqlalchemy_uri: str,
        expose_in_sqllab: bool = True,
        allow_run_async: bool = False,
        allow_csv_upload: bool = True,
        extra: Dict[str, Any] = None
    ) -> DatabaseInfo:
        """创建数据库连接

        Args:
            database_name: 数据库名称
            sqlalchemy_uri: SQLAlchemy 连接字符串
            expose_in_sqllab: 在 SQL Lab 中暴露
            allow_run_async: 允许异步查询
            allow_csv_upload: 允许 CSV 上传
            extra: 额外配置

        Returns:
            创建的数据库信息
        """
        payload = {
            "database_name": database_name,
            "sqlalchemy_uri": sqlalchemy_uri,
            "expose_in_sqllab": expose_in_sqllab,
            "allow_run_async": allow_run_async,
            "allow_csv_upload": allow_csv_upload,
            "extra": json.dumps(extra or {})
        }

        result = self._request("POST", "database/", json=payload)
        item = result.get("result", {})

        return DatabaseInfo(
            id=item["id"],
            name=item["database_name"],
            backend=item.get("backend", "unknown"),
            sqlalchemy_uri=item.get("sqlalchemy_uri", ""),
            expose_in_sqllab=item.get("expose_in_sqllab", True),
            allow_run_async=item.get("allow_run_async", False),
            allow_csv_upload=item.get("allow_csv_upload", True)
        )

    def delete_database(self, database_id: int) -> bool:
        """删除数据库连接

        Args:
            database_id: 数据库 ID

        Returns:
            是否成功
        """
        try:
            self._request("DELETE", f"database/{database_id}")
            return True
        except Exception:
            return False

    # ==================== Schema 发现 ====================

    def get_tables(
        self,
        database_id: int,
        schema: Optional[str] = None,
        force: bool = False
    ) -> List[Dict[str, Any]]:
        """获取数据库表列表

        Args:
            database_id: 数据库 ID
            schema: Schema 名称
            force: 强制刷新缓存

        Returns:
            表信息列表
        """
        params = {}
        if schema:
            params["schema"] = schema
        if force:
            params["force"] = "true"

        result = self._request("GET", f"database/{database_id}/tables/", params=params)
        return result.get("result", [])

    def get_table_columns(
        self,
        database_id: int,
        table_name: str,
        schema: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取表列信息

        Args:
            database_id: 数据库 ID
            table_name: 表名
            schema: Schema 名称

        Returns:
            列信息列表
        """
        params = {"table_name": table_name}
        if schema:
            params["schema"] = schema

        result = self._request("GET", f"database/{database_id}/table/{table_name}/column/", params=params)
        return result.get("result", [])

    def get_table_sample(
        self,
        database_id: int,
        table_name: str,
        schema: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取表样本数据

        Args:
            database_id: 数据库 ID
            table_name: 表名
            schema: Schema 名称
            limit: 返回行数

        Returns:
            样本数据
        """
        params = {"limit": limit}
        if schema:
            params["schema"] = schema

        result = self._request("GET", f"database/{database_id}/table/{table_name}/sample/", params=params)
        return result.get("result", [])

    # ==================== 数据集管理 ====================

    def list_datasets(self) -> List[DatasetInfo]:
        """列出所有数据集

        Returns:
            数据集信息列表
        """
        result = self._request("GET", "dataset/")
        datasets = []

        for item in result.get("result", []):
            datasets.append(DatasetInfo(
                id=item["id"],
                database_id=item["database_id"],
                table_name=item["table_name"],
                schema=item.get("schema"),
                columns=item.get("columns", [])
            ))

        return datasets

    def get_dataset(self, dataset_id: int) -> DatasetInfo:
        """获取数据集详情

        Args:
            dataset_id: 数据集 ID

        Returns:
            数据集信息
        """
        result = self._request("GET", f"dataset/{dataset_id}")
        item = result.get("result", {})

        return DatasetInfo(
            id=item["id"],
            database_id=item["database_id"],
            table_name=item["table_name"],
            schema=item.get("schema"),
            columns=item.get("columns", [])
        )

    def create_dataset(
        self,
        database_id: int,
        table_name: str,
        schema: Optional[str] = None,
        columns: Optional[List[Dict[str, Any]]] = None,
        sql: Optional[str] = None
    ) -> DatasetInfo:
        """创建数据集

        Args:
            database_id: 数据库 ID
            table_name: 表名
            schema: Schema 名称
            columns: 列定义
            sql: SQL 查询（用于虚拟数据集）

        Returns:
            创建的数据集信息
        """
        payload = {
            "database_id": database_id,
            "table_name": table_name,
            "schema": schema,
            "columns": columns or []
        }

        if sql:
            payload["sql"] = sql

        result = self._request("POST", "dataset/", json=payload)
        item = result.get("result", {})

        return DatasetInfo(
            id=item["id"],
            database_id=item["database_id"],
            table_name=item["table_name"],
            schema=item.get("schema"),
            columns=item.get("columns", [])
        )

    def delete_dataset(self, dataset_id: int) -> bool:
        """删除数据集

        Args:
            dataset_id: 数据集 ID

        Returns:
            是否成功
        """
        try:
            self._request("DELETE", f"dataset/{dataset_id}")
            return True
        except Exception:
            return False

    # ==================== SQL 执行 ====================

    def execute_sql(
        self,
        database_id: int,
        sql: str,
        schema: Optional[str] = None,
        limit: int = 1000,
        async_: bool = False
    ) -> Dict[str, Any]:
        """执行 SQL 查询

        Args:
            database_id: 数据库 ID
            sql: SQL 语句
            schema: Schema 名称
            limit: 返回行数限制
            async_: 是否异步执行

        Returns:
            查询结果
        """
        payload = {
            "database_id": database_id,
            "sql": sql,
            "schema": schema,
            "queryLimit": limit,
            "runAsync": async_
        }

        result = self._request("POST", f"database/{database_id}/query/", json=payload)
        return result.get("result", {})

    @classmethod
    def from_env(cls) -> "DatabaseManager":
        """从环境变量创建实例

        Returns:
            DatabaseManager 实例
        """
        auth = SupersetAuth.from_env()
        return cls(auth=auth)


# 支持的数据库连接字符串模板
DATABASE_URI_TEMPLATES = {
    "postgresql": "postgresql://{username}:{password}@{host}:{port}/{database}",
    "mysql": "mysql+pymysql://{username}:{password}@{host}:{port}/{database}",
    "sqlite": "sqlite:///{path}",
    "clickhouse": "clickhouse+native://{username}:{password}@{host}:{port}/{database}",
    "bigquery": "bigquery://{project_id}",
    "snowflake": "snowflake://{username}:{password}@{account}/{database}?warehouse={warehouse}",
    "redshift": "redshift+psycopg2://{username}:{password}@{host}:{port}/{database}",
    "presto": "presto://{host}:{port}/{catalog}/{schema}",
    "trino": "trino://{host}:{port}/{catalog}/{schema}",
    "hive": "hive://{host}:{port}/{database}",
    "databricks": "databricks://token:{token}@{host}/{database}",
}


def main():
    """CLI 入口"""
    import argparse

    parser = argparse.ArgumentParser(description="Superset 数据连接器")
    parser.add_argument("command", choices=["list", "add", "tables", "schema", "query", "create-dataset"])
    parser.add_argument("--name", help="数据库名称")
    parser.add_argument("--uri", help="SQLAlchemy URI")
    parser.add_argument("--database-id", type=int, help="数据库 ID")
    parser.add_argument("--table", help="表名")
    parser.add_argument("--sql", help="SQL 查询")
    parser.add_argument("--json", action="store_true", help="JSON 输出")

    args = parser.parse_args()

    manager = DatabaseManager.from_env()

    if args.command == "list":
        databases = manager.list_databases()
        for db in databases:
            if args.json:
                print(json.dumps({"id": db.id, "name": db.name, "backend": db.backend}))
            else:
                print(f"[{db.id}] {db.name} ({db.backend})")

    elif args.command == "add":
        if not args.name or not args.uri:
            print("错误: 需要 --name 和 --uri")
            return

        db = manager.create_database(args.name, args.uri)
        print(f"创建成功: [{db.id}] {db.name}")

    elif args.command == "tables":
        if not args.database_id:
            print("错误: 需要 --database-id")
            return

        tables = manager.get_tables(args.database_id)
        for table in tables:
            if args.json:
                print(json.dumps(table))
            else:
                print(f"{table.get('schema', '')}.{table.get('table', '')}")

    elif args.command == "schema":
        if not args.database_id or not args.table:
            print("错误: 需要 --database-id 和 --table")
            return

        columns = manager.get_table_columns(args.database_id, args.table)
        for col in columns:
            print(f"{col['column_name']}: {col['type']}")

    elif args.command == "query":
        if not args.database_id or not args.sql:
            print("错误: 需要 --database-id 和 --sql")
            return

        result = manager.execute_sql(args.database_id, args.sql)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "create-dataset":
        if not args.database_id or not args.table:
            print("错误: 需要 --database-id 和 --table")
            return

        dataset = manager.create_dataset(args.database_id, args.table)
        print(f"创建成功: [{dataset.id}] {dataset.table_name}")


if __name__ == "__main__":
    main()