class School:
    def __init__(self, name):
        self.name = name          # 学校名称
        self.colleges = set()    # 学院集合,使用set避免重复
        self.students = {}       # Students
    
    # College Operations
    
    def add_college(self, college_name):
        #添加学院
        if college_name in self.colleges:
            raise ValueError(f"College '{college_name}' already exists")
        self.colleges.add(college_name)
        return college_name
    
    def delete_college(self, college_name):
        #删除学院
        if college_name not in self.colleges:
            raise ValueError(f"College '{college_name}' doesn't exist")
        
        # Check if the college has any students
        if any(student['college'] == college_name for student in self.students.values()):
            raise ValueError(f"Cannot delete college '{college_name}' as it still has students")
            
        self.colleges.remove(college_name)
        return True
    
    def update_college(self, old_name, new_name):
        #更新学院名称
        if old_name not in self.colleges:
            raise ValueError(f"College '{old_name}' doesn't exist")
        if new_name in self.colleges:
            raise ValueError(f"College name '{new_name}' already exists")
        
        # Update college name in student records
        for student in self.students.values():
            if student['college'] == old_name:
                student['college'] = new_name
        
        self.colleges.remove(old_name)
        self.colleges.add(new_name)
        return new_name
    
    def get_colleges(self):
        #获取所有学院
        return list(self.colleges)
    
    def has_college(self, college_name):
        #检查学院是否存在
        return college_name in self.colleges
    
    # Student Operations
    
    def add_student(self, student_id, first_name, last_name, college_name):
        #添加学生
        if student_id in self.students:
            raise ValueError(f"Student ID '{student_id}' already exists")
        if college_name not in self.colleges:
            raise ValueError(f"College '{college_name}' doesn't exist")
        
        self.students[student_id] = {
            'first_name': first_name,
            'last_name': last_name,
            'college': college_name
        }
        return self.students[student_id]
    
    def delete_student(self, student_id):
        #删除学生
        if student_id not in self.students:
            raise ValueError(f"Student ID '{student_id}' doesn't exist")
        del self.students[student_id]
        return True
    
    def update_student(self, student_id, first_name=None, last_name=None, college_name=None):
        #更新学生信息
        if student_id not in self.students:
            raise ValueError(f"Student ID '{student_id}' doesn't exist")
        
        student = self.students[student_id]
        if college_name and college_name not in self.colleges:
            raise ValueError(f"College '{college_name}' doesn't exist")
        
        if first_name:
            student['first_name'] = first_name
        if last_name:
            student['last_name'] = last_name
        if college_name:
            student['college'] = college_name
        
        return student
    
    def get_student(self, student_id):
        #获取学生信息
        if student_id not in self.students:
            raise ValueError(f"Student ID '{student_id}' doesn't exist")
        return self.students[student_id]
    
    def get_full_name(self, student_id):
        #获取学生全名
        student = self.get_student(student_id)
        return f"{student['last_name']} {student['first_name']}"
    
    def list_students(self, college_name=None):
        #列出学生，可按学院筛选
        if college_name and college_name not in self.colleges:
            raise ValueError(f"College '{college_name}' doesn't exist")
        
        if college_name:
            return {id: s for id, s in self.students.items() if s['college'] == college_name}
        return self.students.copy()


# 示例
if __name__ == "__main__":
    # 创建学校
    my_school = School("A University")
    
    print("College example")
    # 添加学院
    my_school.add_college("College of Literature")
    my_school.add_college("College of Science")
    print("All colleges:", my_school.get_colleges())
    
    # 更新学院名
    my_school.update_college("College of Literature", "College of Literature and Media")
    print("Updated colleges:", my_school.get_colleges())
    
    print("\nStudent operations example")
    # 添加学生
    my_school.add_student("101", "Ame", "Johnson", "College of Literature and Media")
    my_school.add_student("102", "Michael", "Williams", "College of Science")
    my_school.add_student("103", "Sara", "Brown", "College of Science")
    
    # 列出所有学生
    print("All students:")
    for id, student in my_school.list_students().items():
        print(f"{id}: {student['last_name']} {student['first_name']} ({student['college']})")
    
    # 更新学生
    my_school.update_student("101", last_name="Davis")
    print("\nUpdated student 101:", my_school.get_student("101"))
    print("Full name of student 101:", my_school.get_full_name("101"))
    
    # 按学院筛选学生
    print("\nStudents in College of Science:")
    for id, student in my_school.list_students("College of Science").items():
        print(f"{id}: {student['last_name']} {student['first_name']}")
    
    # 删除学生
    my_school.delete_student("102")
    print("\nStudents after deleting 102:")
    for id in my_school.list_students():
        print(f"{id}: {my_school.get_full_name(id)}")