import pyxel

def rgb(r, g, b):
    return 256*256*r+256*g+b

def interpolate_color(color1, color2, percentage):
    r = int(color1[0] + (color2[0] - color1[0]) * percentage)
    g = int(color1[1] + (color2[1] - color1[1]) * percentage)
    b = int(color1[2] + (color2[2] - color1[2]) * percentage)

    return (r,g,b)

FPS = 60

class Fuel:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 9
        self.h = 12

    def collision(self, player):
        if player.x + player.w > self.x and player.x < self.x + self.w:
            if player.y + player.h > self.y and player.y < self.y + self.h:
                return True
        return False

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 35, 187, self.w, self.h, colkey=False)

class FuelGauge:
    def __init__(self, w, h, c):
        self.w = w
        self.h = h
        self.c = c
        self.fuel = .7

    def reduce(self, x):
        self.fuel = max(self.fuel - x, 0)

    def augment(self, x):
        self.fuel = min(self.fuel + x, 1)

    def draw(self, x, y):
        pyxel.rect(x, y, self.w, self.h, self.c)
        border_size = 1
        pyxel.rect(x + border_size, y + border_size, self.w - 2 * border_size, self.h - 2 * border_size, 0)
        gauge_height = (self.h - 2 * border_size)
        pyxel.rect(x + border_size, y + border_size + gauge_height * (1-self.fuel), self.w - 2 * border_size, gauge_height * self.fuel, 4)

class Platform:
    def __init__(self, x):
        self.x = x
        y = -0.3*x
        self.y = round(pyxel.rndf(y * 0.5, y * 1.5))
        self.w = 64
        self.h = 3

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 0, 63, self.w, self.h, colkey=False)
    
    def distance(self, player):
        return pyxel.sqrt((self.x- player.x)**2+(self.y - player.y)**2)
    
class Asteroid():

    SPEED = 2

    def __init__(self, x, y):
        self.x = x
        self.y = y
        
        self.w = 13
        self.h = 12

    def upate(self):
        self.x += self.SPEED
        self.y += self.SPEED

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 0, 40, self.w, self.h, colkey=False)

class Player:

    SPEED = 2
    GRAVITY = 0.75

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 13
        self.h = 11

        self.x_vel = 0
        self.y_vel = 0
        self.fall_count = 0
        self.fly_count = 0
        self.direction = 1

    def move_right(self):
        self.x_vel = self.SPEED
        self.direction = 1

    def move_left(self):
        self.x_vel = -self.SPEED
        self.direction = -1

    def jump(self):
        self.y_vel = -self.GRAVITY * (2 + self.fly_count * 0.05)
        self.fly_count += 1
        self.fall_count = 0

    def xCollision(self, object):
        if self.x + self.w > object.x + self.x_vel and self.x< object.x + object.w + self.x_vel:
            return True
        return False

    def yCollision(self, object):
        if object.y < self.y + self.h + self.y_vel and object.y + object.h > self.y + self.y_vel:
            return True
        return False

    def update(self, platforms):

        if pyxel.btnr(pyxel.KEY_SPACE): self.fly_count = 0
        
        self.y_vel += min(1, ((self.fall_count / 2) / FPS) * self.GRAVITY)

        self.fall_count += 1

        closest_platform = platforms[0]
        for platform in platforms:
            if platform.distance(self) < closest_platform.distance(self):
                closest_platform = platform

        if self.yCollision(closest_platform):
            if self.xCollision(closest_platform):
                # Bottom Collision
                if self.y + self.h <= closest_platform.y:
                    self.y = closest_platform.y - self.h
                    self.y_vel = 0
                    self.fall_count = 0
                # Top Collision
                else:
                    self.y = closest_platform.y + closest_platform.h
                    self.y_vel = 0
                    self.fly_count = 0
            else:
                self.x_vel = 0

        self.y += round(self.y_vel)
        self.x += round(self.x_vel)
        self.x_vel = 0

        pyxel.camera(self.x - pyxel.width/2 + self.w/2, self.y - pyxel.height/2 + self.h/2)

    def draw(self):
        if self.fly_count > 0:
            pyxel.blt(self.x, self.y, 0, 2, 25, self.w*self.direction, self.h, colkey=False)
        else:
            pyxel.blt(self.x, self.y, 0, 2, 9, self.w*self.direction, self.h, colkey=False)


class App:
    def __init__(self):
        pyxel.init(256, 256, title="Pyxel Platformer", fps=FPS)
        pyxel.load("3.pyxres")

        self.fuelChance = 0.5
        self.bestScore = 0
        pyxel.colors[15] = rgb(0,0,0)

        self.initGame()

        pyxel.run(self.update, self.draw)

    def initGame(self):
        self.asteroid_count = 0
        self.last_platform = 200
        self.platform_count = 1
        self.player = Player(0, -60)
        self.platforms = [Platform(0), Platform(self.last_platform)]
        self.asteroids = []
        self.fuels = [Fuel(self.platforms[0].w/2, -10)]
        self.fuelGauge = FuelGauge(10, 50, 3)

    def update(self):

        if self.player.y > 20 or any([self.player.xCollision(asteroid) and self.player.yCollision(asteroid) for asteroid in self.asteroids]):
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.initGame()
            return

        # Add New Platform
        if self.player.x > self.last_platform:
            self.last_platform += 100 + (self.platform_count * 20)
            self.platforms.append(Platform(self.last_platform))
            if pyxel.rndf(0,1) < self.fuelChance:
                self.fuels.append(Fuel(self.platforms[-1].x + self.platforms[-1].w//2, self.platforms[-1].y - 9))
                self.fuelChance = 0.5
            else:
                self.fuelChance += 0.2
            
            self.platform_count += 1

        if pyxel.btn(pyxel.KEY_LEFT):
            self.player.move_left()

        if pyxel.btn(pyxel.KEY_RIGHT):
            self.player.move_right()

        if pyxel.btn(pyxel.KEY_SPACE) and self.fuelGauge.fuel > 0:
            self.fuelGauge.reduce(0.005)
            self.player.jump()

        if pyxel.btn(pyxel.KEY_K):
            self.fuelGauge.augment(1)

        for fuel in self.fuels:
            if fuel.collision(self.player):
                self.fuelGauge.augment(1)
                self.fuels.remove(fuel)

        self.player.update(self.platforms)
        
        self.asteroid_count += 1
        for asteroid in self.asteroids:
            asteroid.upate()

        if self.asteroid_count%(200/(len(self.platforms)-1)) == 0:
            x_pos = pyxel.rndi(round(self.player.x - pyxel.width), round(self.player.x))
            self.asteroids.append(Asteroid(x_pos, self.player.y - pyxel.height/2))

        r, g, b = interpolate_color((135,206,235), (19,24,98), 0.05 * (len(self.platforms) - 2))
        pyxel.colors[1] = rgb(r, g, b)

    def draw(self):
        pyxel.cls(1)
        self.player.draw()
        for platform in self.platforms:
            platform.draw() 

        for fuel in self.fuels:
            fuel.draw()

        self.fuelGauge.draw(self.player.x - 110, self.player.y + 40)

        first = self.platforms[-2]
        second = self.platforms[-1]
        pyxel.line(first.x + first.w, first.y, second.x, second.y, 0)

        top_x = self.player.x - pyxel.width/2 + self.player.w/2 + 10
        top_y = self.player.y - pyxel.height/2 + self.player.h/2 + 10

        pyxel.text(top_x, top_y, f'Score : {len(self.platforms) -2}', 0)

        for asteroid in self.asteroids:
            asteroid.draw()

        pyxel.text(-100, -50, 'Arrow Keys to move', 7)
        pyxel.text(-100, -60, 'Space to jump', 7)
        pyxel.text(-100, -70, f"Best score : {self.bestScore}", 7)

        if self.player.y > 20 or any([self.player.xCollision(asteroid) and self.player.yCollision(asteroid) for asteroid in self.asteroids]):
            pyxel.colors[1] = rgb(100, 100, 100)
            pyxel.text(self.player.x - 10, self.player.y, 'You dead', 0)
            if len(self.platforms)-2 > self.bestScore:
                self.bestScore = len(self.platforms)-2
            pyxel.text(self.player.x - 35, self.player.y + 10, 'Press [Space] to restart', 0)
            

App()