import mysql.connector
from mysql.connector import Error

# 1. 数据库连接与创建
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root'
        )
        return connection
    except Error as e:
        print(f"连接MySQL数据库失败: {e}")
        return None

def create_database(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS schooldb")
        cursor.execute("USE schooldb")
        
        # 建表语句（学校、学院、学生）
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS school (
            school_id INT AUTO_INCREMENT PRIMARY KEY,
            school_name VARCHAR(100) NOT NULL UNIQUE
        )""")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS college (
            college_id INT AUTO_INCREMENT PRIMARY KEY,
            college_name VARCHAR(100) NOT NULL,
            school_id INT,
            FOREIGN KEY (school_id) REFERENCES school(school_id)
        )""")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS student (
            student_id INT AUTO_INCREMENT PRIMARY KEY,
            student_name VARCHAR(50) NOT NULL,
            school_id INT,
            college_id INT,
            FOREIGN KEY (school_id) REFERENCES school(school_id),
            FOREIGN KEY (college_id) REFERENCES college(college_id)
        )""")
        
        print("数据库和表创建成功")
    except Error as e:
        print(f"创建数据库失败: {e}")
    finally:
        if connection.is_connected():
            cursor.close()

#2. 增删改查操作
#2.1 增
#添加学校
def add_school(connection, school_name):
    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO school (school_name) VALUES (%s)", (school_name,))
        connection.commit()
        print(f"学校 '{school_name}' 添加成功")
    except Error as e:
        print(f"添加学校失败: {e}")

#添加学院
def add_college(connection, college_name, school_name):
    try:
        cursor = connection.cursor()
        # 先查询学校ID
        cursor.execute("SELECT school_id FROM school WHERE school_name = %s", (school_name,))
        school_id = cursor.fetchone()
        if school_id:
            cursor.execute(
                "INSERT INTO college (college_name, school_id) VALUES (%s, %s)",
                (college_name, school_id[0])
            )
            connection.commit()
            print(f"学院 '{college_name}' 添加成功")
        else:
            print(f"学校 '{school_name}' 不存在")
    except Error as e:
        print(f"添加学院失败: {e}")

#添加学生
def add_student(connection, student_name, school_name, college_name=None):
    try:
        cursor = connection.cursor()
        # 查询学校ID
        cursor.execute("SELECT school_id FROM school WHERE school_name = %s", (school_name,))
        school_id = cursor.fetchone()
        
        if not school_id:
            print(f"学校 '{school_name}' 不存在")
            return
        
        college_id = None
        if college_name:
            # 查询学院ID
            cursor.execute(
                "SELECT college_id FROM college WHERE college_name = %s AND school_id = %s",
                (college_name, school_id[0])
            )
            college_id = cursor.fetchone()
            if college_id:
                college_id = college_id[0]
            else:
                print(f"学院 '{college_name}' 不存在")
                return
        
        cursor.execute(
            "INSERT INTO student (student_name, school_id, college_id) VALUES (%s, %s, %s)",
            (student_name, school_id[0], college_id)
        )
        connection.commit()
        print(f"学生 '{student_name}' 添加成功")
    except Error as e:
        print(f"添加学生失败: {e}")

# 2.2 查
def query_all(connection):
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
        SELECT 
            s.school_name,
            c.college_name,
            st.student_name
        FROM 
            school s
        LEFT JOIN 
            college c ON s.school_id = c.school_id
        LEFT JOIN 
            student st ON s.school_id = st.school_id 
            AND (c.college_id = st.college_id OR st.college_id IS NULL)
        ORDER BY 
            s.school_name, c.college_name, st.student_name
        """)
        
        results = cursor.fetchall()
        print("\n所有学校、学院和学生:")
        print("-" * 50)
        for row in results:
            print(f"学校: {row['school_name'] or 'NULL'}, "
                  f"学院: {row['college_name'] or 'NULL'}, "
                  f"学生: {row['student_name'] or 'NULL'}")
        print("-" * 50)
        return results
    except Error as e:
        print(f"查询失败: {e}")
        return None
    
# 2.3 改
def update_student(connection, student_name, new_name=None, new_school=None, new_college=None):
    try:
        cursor = connection.cursor()
        
        # 查询学生当前信息
        cursor.execute("SELECT student_id, school_id, college_id FROM student WHERE student_name = %s", (student_name,))
        student = cursor.fetchone()
        
        if not student:
            print(f"学生 '{student_name}' 不存在")
            return
        
        student_id, school_id, college_id = student
        
        # 更新学生姓名
        if new_name:
            cursor.execute("UPDATE student SET student_name = %s WHERE student_id = %s", (new_name, student_id))
        
        # 更新学校
        if new_school:
            cursor.execute("SELECT school_id FROM school WHERE school_name = %s", (new_school,))
            new_school_id = cursor.fetchone()
            if new_school_id:
                cursor.execute("UPDATE student SET school_id = %s WHERE student_id = %s", (new_school_id[0], student_id))
            else:
                print(f"学校 '{new_school}' 不存在")
        
        # 更新学院
        if new_college:
            if not new_school and not school_id:
                print("无法更新学院，学生没有关联学校")
                return
            
            school_id_to_use = school_id
            if new_school:
                cursor.execute("SELECT school_id FROM school WHERE school_name = %s", (new_school,))
                school_id_to_use = cursor.fetchone()[0]
            
            cursor.execute(
                "SELECT college_id FROM college WHERE college_name = %s AND school_id = %s",
                (new_college, school_id_to_use)
            )
            new_college_id = cursor.fetchone()
            if new_college_id:
                cursor.execute("UPDATE student SET college_id = %s WHERE student_id = %s", (new_college_id[0], student_id))
            else:
                print(f"学院 '{new_college}' 不存在")
        
        connection.commit()
        print(f"学生信息更新成功")
    except Error as e:
        print(f"更新学生信息失败: {e}")

#2.4 删
# 删除学生
def delete_student(connection, student_name):
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM student WHERE student_name = %s", (student_name,))
        connection.commit()
        print(f"学生 '{student_name}' 删除成功")
    except Error as e:
        print(f"删除学生失败: {e}")

#删除学院
def delete_college(connection, college_name):
    try:
        cursor = connection.cursor()
        # 先删除关联的学生
        cursor.execute("""
        DELETE FROM student 
        WHERE college_id IN (
            SELECT college_id FROM college WHERE college_name = %s
        )
        """, (college_name,))
        # 再删除学院
        cursor.execute("DELETE FROM college WHERE college_name = %s", (college_name,))
        connection.commit()
        print(f"学院 '{college_name}' 及其关联学生删除成功")
    except Error as e:
        print(f"删除学院失败: {e}")

#删除学校
def delete_school(connection, school_name):
    """删除学校"""
    try:
        cursor = connection.cursor()
        # 先查询学校ID
        cursor.execute("SELECT school_id FROM school WHERE school_name = %s", (school_name,))
        school_id = cursor.fetchone()
        
        if not school_id:
            print(f"学校 '{school_name}' 不存在")
            return
        
        # 先删除关联的学生
        cursor.execute("DELETE FROM student WHERE school_id = %s", (school_id[0],))
        # 再删除关联的学院
        cursor.execute("DELETE FROM college WHERE school_id = %s", (school_id[0],))
        # 最后删除学校
        cursor.execute("DELETE FROM school WHERE school_id = %s", (school_id[0],))
        connection.commit()
        print(f"学校 '{school_name}' 及其关联的学院和学生删除成功")
    except Error as e:
        print(f"删除学校失败: {e}")
# 清理所有剩余数据
def cleanup_database(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM student")
        cursor.execute("DELETE FROM college")
        cursor.execute("DELETE FROM school")
        connection.commit()
        print("Database cleaned up successfully")
    except Error as e:
        print(f"Failed to clean up database: {e}")


def main():
    # 创建连接
    connection = create_connection()
    if not connection:
        return
    
    try:
        # 初始化数据库
        create_database(connection)
        
        print("\n增删改查示例\n")
        
        # 1. 增操作
        print("1. 添加数据:")
        add_school(connection, "A大学")
        add_school(connection, "B大学")
        
        add_college(connection, "计算机学院", "A大学")
        add_college(connection, "经济学院", "A大学")
        add_college(connection, "法学院", "B大学")
        
        add_student(connection, "张三", "A大学", "计算机学院")
        add_student(connection, "李四", "A大学", "经济学院")
        add_student(connection, "王五", "B大学", "法学院")
        add_student(connection, "赵六", "B大学") 
        
        # 2. 查操作
        print("\n2. 查询所有数据:")
        query_all(connection)
        
        # 3. 改操作
        print("\n3. 修改数据:")
        # 修改学生姓名
        update_student(connection, "张三", new_name="张三四")
        # 修改学生学校和学院
        update_student(connection, "李四", new_school="B大学", new_college="法学院")
        query_all(connection)  # 再次查询查看修改结果
        
        # 4. 删操作
        print("\n4. 删除数据:")
        # 删除学生
        delete_student(connection, "赵六")
        # 删除学院(会同时删除关联的学生)
        delete_college(connection, "计算机学院")
        # 删除学校(会同时删除关联的学院和学生)
        delete_school(connection, "A大学")
        delete_school(connection, "B大学")
        
        print("\n5. 最终数据状态:")
        query_all(connection)
        
    finally:
        if connection.is_connected():
            connection.close()

if __name__ == "__main__":
    main()