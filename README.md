![游戏运行中时的图片](http://upload-images.jianshu.io/upload_images/5290846-3cc4a0b20bce147e.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

### 游戏规则：
 鼠标控制你的白球，红球每隔两秒从四个边界随机出现，速度的大小和速度也是随机的，红球每隔5秒就消失，红球碰到你的白球就gameover。

### 写游戏中要思考的地方：
 - 如何方便的由白球的图片得出红球的图片
 - 如何灵活控制红球的速度
 - 如何让红球碰到边界就反弹，如何让红球互相碰到也反弹
 - 游戏是通过不断更新两种球的位置进行的，同时也要每隔两秒出现新的红球，怎样好的控制这一点。

### 游戏运行的逻辑：
  - 遍历获取事件：
  ```
        while True:
            if self.state != self.nextState:
                self.state = self.nextState
                self.state.firstDisplay(screen)

            for event in pygame.event.get():
                self.state.handle(event)
            self.state.update(self)

            self.state.display(screen)
  ```
  - 其中游戏拥有很多state类，且都有nextstate指向另一个state，类似于C的指针。通过用户事件或游戏事件，游戏的state不断变为下一个state来促使游戏的发展。

  - 其中收集合适的图片素材也是问题，白球的图片是找来的。红球的图片是通过PIL库，将它转为RGBA模式后，分为四个通道，再新建一张相同大小的黑色图片，取出其G和B通道，混合后就成为一张红球：

```
from PIL import Image
white_ball = Image.open('images/white_ball.png')
white_img = white_ball.convert("RGBA")
bands = white_img.split()

black_img = Image.new("RGBA", white_ball.size, (0, 0, 0))
other_bands = black_img.split()

red_ball = Image.merge("RGBA", (bands[0], other_bands[1], other_bands[2], bands[3]))
red_ball.save("images/red_ball.png", 'png')
```

  - 因为红球的速度是四面八方的，而pygame只让你控制上下左右，为了便于控制，我做了一个向量类：
```
class Vector2(object):
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def __str__(self):
        return "(%s, %s)" % (self.x, self.y)
    __repr__ = __str__

    def __add__(self, other):
        return Vector2(self.x+other.x, self.y+other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, num):
        return Vector2(num*self.x, num*self.y)

    def __divmod__(self, scalar):
        return Vector2(self.x / scalar, self.y / scalar)

    def get_length(self):
        from math import sqrt
        return sqrt(self.x**2 + self.y**2)

    def normolize(self):
        length = self.get_length()
        return Vector2(self.x/length, self.y/length)

    @classmethod
    def from_points(cls, P1, P2):
        return cls(P2[0] - P1[0], P2[1] - P1[1])
```
  - 游戏中遇到的最大的问题是，控制红球之间碰撞后碰开，也就是速度取反。pygame有一个 pygame.Rect.colliderect函数，可以判断两张图是否有重叠部分。所以我的Ball类（两种球的父类）有一个touches方法：
```
    def touches(self, other):
        return self.rect.colliderect(other.rect)
```
用这个判断白球死亡没问题，因为红白有重叠后游戏就结束了。
但用这个来让红球互相碰撞后反弹就有问题了，因为反弹我是设置的速度乘 -1,但我判断是取的一个O(n^2)的算法，因为红球一般最多也就五六个（事实上现在的我也很难想到更好的)：
```
        for a_red_ball in self.red_sprites:
            for another_red_ball in self.red_sprites:
                if a_red_ball is not another_red_ball and a_red_ball.touches(another_red_ball):
                    a_red_ball.speed = a_red_ball.speed * (-1)
                    another_red_ball.speed = another_red_ball.speed * (-1)

                    a_red_ball.play_bounce_sound()
```
但这样有个问题，很明显就是每个球的速度都要乘两次-1。解决办法是给球加个be_bounce+False的属性，然后：
```
        for a_red_ball in self.red_sprites:
            for another_red_ball in self.red_sprites:
                if a_red_ball is not another_red_ball and a_red_ball.touches(another_red_ball) and \
                        not (a_red_ball.be_bounce and another_red_ball.be_bounce):
                    a_red_ball.speed = a_red_ball.speed * (-1)
                    another_red_ball.speed = another_red_ball.speed * (-1)
                    a_red_ball.be_bounce = True
                    another_red_ball.be_bounce = True
                    a_red_ball.play_bounce_sound()

        for red_ball in self.red_sprites:
            red_ball.be_bounce = False
```
代码很好懂，就不解释了。

- 还有个问题就是如何在所有球位置不断更新的时候出现新的球，我的解决办法是给游戏运行进程的一个state加一个gap属性，默认是0，更新位置的时候让它不断加上过去的时间，满两秒出现新的球，然后再设置为0：

```
self.gap += time_passed_seconds
        if int(self.gap) == 2:
            new_ball = RedBall(self.red_ball_image)
            now_sprite = pygame.sprite.RenderUpdates(new_ball)
            self.red_sprites.add(now_sprite)
            self.gap = 0
```

最后再吐槽一下pygame官方文档做的真的有点差劲，有些东西我都是猜测应该有这种用法，官方文档并没有说明。
