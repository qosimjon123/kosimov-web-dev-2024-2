from flask_login import current_user


class CheckRights:
    def __init__(self, record):
        self.record = record

    def create(self):
        return current_user.is_admin()

    def edit(self):
        if current_user.id == self.record.id:
            return True
        return current_user.is_admin()

    def delete(self):
        return current_user.is_admin()

    def show(self):
        if current_user.id == self.record.id:
            return True
        return current_user.is_admin()
    
    # def edit_role(self):
    #     return current_user.is_admin()
    def show_logs(self):
        return current_user.is_admin()
