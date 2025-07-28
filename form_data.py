class FormData:
    def __init__(self, categoryId, parentId, categoryName):
        self.categoryId = categoryId
        self.parentId = parentId
        self.categoryName = categoryName

        self.pointPrice = 10.00
        self.downType = 2
        self.attachAttrFormat = ""
        self.attachAttrNum = 0
        self.attachAttrSize = 0
        self.title = ""
        self.content = ""
        self.filterDetailCode1 = ""
        self.filterDetailCode2 = ""
        self.status = 1
        self.isTop = 0
        self.openJili = 0
        self.vipOnly = 1
    
    def to_dict(self):
        """将对象转为字典"""
        return {
            'categoryId': self.categoryId,
            'parentId': self.parentId,
            'categoryName': self.categoryName,
            'pointPrice': self.pointPrice,
            'downType': self.downType,
            'attachAttrFormat': self.attachAttrFormat,
            'attachAttrNum': self.attachAttrNum,
            'attachAttrSize': self.attachAttrSize,
            'title': self.title,
            'content': self.content,
            'filterDetailCode1': self.filterDetailCode1,
            'filterDetailCode2': self.filterDetailCode2,
            'status': self.status,      
            'isTop': self.isTop,
            'openJili': self.openJili,
            'vipOnly': self.vipOnly
        }