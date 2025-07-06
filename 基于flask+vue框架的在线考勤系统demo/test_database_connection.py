import logging
from flask_sqlalchemy import SQLAlchemy
from app.models_kq.user import Employee_KQ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
db = SQLAlchemy()
def test_database_connection():
    try:
        test_employee = Employee_KQ.query.first()
        if test_employee:
            logger.info("数据库连接成功，查询到员工记录: %s", test_employee)
        else:
            logger.info("数据库连接成功，但没有找到员工记录")
    except Exception as e:
        logger.error("数据库连接失败: %s", e)

if __name__ == "__main__":
    test_database_connection()