class AttackEffect:
    def __init__(self, start_pos, target_pos, image, speed=10):
        self.image = image
        self.pos = list(start_pos)
        self.target = list(target_pos)
        self.speed = speed
        self.active = True
        self.exploding = False
        self.timer = 15  # 持续时间

    def update(self):
        if not self.active:
            return
        if self.exploding:
            self.timer -= 1
            if self.timer <= 0:
                self.active = False
            return

        dx = self.target[0] - self.pos[0]
        dy = self.target[1] - self.pos[1]
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance < self.speed:
            self.pos = self.target
            self.exploding = True
        else:
            self.pos[0] += self.speed * dx / distance
            self.pos[1] += self.speed * dy / distance

    def draw(self, screen):
        if self.active:
            screen.blit(self.image, self.pos)
