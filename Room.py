import pygame
import Enemy
class TheRoom:
    def __init__(self, EnemyList, AllEnemyID,ClassMap, Doors, Cleared):
        #give Allenemyid as a list of tuples, the first element will be the id of the enemy and the second element will be the name of the enemy which will then be loaded
        self.EnemyList = EnemyList
        self.AllEnemyID = AllEnemyID
        self.doors = Doors
        self.Cleared = Cleared
        self.LeClassMap = ClassMap
    def LoadRoom(self, Doors):
        for i in range(len(self.EnemyList)):
            EnemyStr = str(self.AllEnemyID[i][1])
            print("enemy str is " + EnemyStr)
            self.EnemyList[i] = self.LeClassMap[EnemyStr](100, 200, (100, 200), (100, 100))
            #this allows us to load in all the enemies
           # self.EnemyList[i] = Enemy.

TheClassmap = {cls.__name__: cls for cls in Enemy.BaseEnemy.__subclasses__()}
MyRoom = TheRoom([1],[(1, "Phonk")], TheClassmap,"Hi", False)
MyRoom.LoadRoom(MyRoom.doors)