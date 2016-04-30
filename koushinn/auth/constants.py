# -*- coding: utf-8 -*-

class Permission:
    """
    使用位运算标记用户权限
    每一位表示一种权限
    """
    BLOCKED = 0x00
    READ = 0x01
    MANUEL_PUSH = 0x02
    ADMINISTER = 0x80


class Opration:
    BAN = 1
    DELETE = 2
    PUSH = 3
