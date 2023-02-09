## requriements:
##pip3 install vpython
##pip3 install pygame

import vpython as v
import random
import pygame

class Game:
    scene1 = v.canvas(title="Doppeldecker",
                      width=800,
                      height=600,
                      center=v.vector(0, 0, 0),
                      background=v.vector(0.8, 0.8, 1),
                      resizable=False
                      )
    #following Camera behind 
    scene1.autoscale = False
    scene1.userspin = False
    camera_delay = 0.1 # seconds
    camera_history = []
    # scene1.range = 200
    max_depth = -10 # lowest point of the landscape
    dt = 0.005  # delta time
    world = 100 # half lenght (x,y) of world
    rotation = 60  # rotation speed of plane
    cooldown_gun = 0.05
    cooldown_flak = 0.20
    cooldown_bomb = 0.3
    cooldown_rocket = 0.12
    drag_player = 5.5 # 5.515
    drag_bullet = 0.1
    drag_bomb = 2.0
    radius_player = 0.15 # for ground collision hitbox
    cannon_power = 17000 # bullet speed at start
    rocket_power = 0.25
    rocket_fuel = 0.5 # sec
    lift_factor = 0.5
    mass_player = 0.1
    mass_bullet = 0.011
    mass_bomb = 0.05
    mass_rocket = 0.03
    mass_particle = 0.005
    flak_range = 40 # range when flak start shooting at player
    flak_crit_distance = 0.5  # how close flak shell must be to player center to make damage
    g = 9.81 #earth's gravitional pull
    #g_player = 9.81
    #g_bullet = 9.81
    #g_bomb = 5.2
    particle_list = []
    tank_list = []
    bullet_list = []
    explosion_list = []
    static_list = []
    bomb_list = []
    rocket_list = []
    target_list = []
    ring_list = []
    #flak_list = []
    flak_barrel_list = []
    ring_center_distance = 1  # 1 is hard, 10 is super easy
    # UI widgets, initialized in function main()
    vlist = [] # list for ground vertices
    label_dt = None
    label_lift = None
    label_ring_center_distance = None
    label_rotation = None
    label_delay = None
    ring_index = 0
    my_ring = None
    max_power = 20 #values over 20 make the plane slower
    min_power = 0

def create_sun():
    s = v.simple_sphere(
            pos = v.vector(random.uniform(-Game.world,Game.world),  # x
                           random.uniform(50,60),                   # y
                           random.uniform(-Game.world,Game.world)   # z
                           ),
            radius = random.uniform(0.5, 2.5),  # 0.5 until 2.5
            color = v.vector(1,1,0),    #100%red, 100%green, 0%blue = yellow
            shininess = 0.6,  #shine
            emissive = True,  #glows
        )
    return s

def create_ring():
    r = v.ring(
        pos = v.vector(random.uniform(-Game.world,Game.world),
                       random.uniform(20, 30),
                       random.uniform(-Game.world, Game.world),
                       ),
        radius = random.uniform(100, 500),
        color = v.vector(0, 0, 1),
        shininess = 0.3,
        emissive = False,
        )
    return r

def create_building():
    b = v.box(
        pos = v.vector(50, 100, 50),
        color = v.vector(1, 1, 0.7)
        )
    return b

def create_bullet():
    bullet = v.simple_sphere(
            radius = random.uniform(0.1, 0.1),  # 0.5 until 2.5
            color = v.vector(0,0,1),    #100%red, 100%green, 0%blue = yellow
            shininess = 0.1,  #shine
            emissive = True,  #glow
            )
    return bullet

def create_rocket():
    rocket = v.simple_sphere(
            radius = random.uniform(0.1, 0.1),  # 0.5 until 2.5
            color = v.vector(1,1,1),    #100%red, 100%green, 0%blue = yellow
            shininess = 0.1,  #shine
            emissive = True,  #glow
            )
    return rocket


def create_flak():
    h = random.randint(5,12) # height
    body = v.box(
        size=v.vector(0.5,h,0.5),
        pos= v.vector(2,h/2,2),
        axis = v.vector(1,0,0),
        color = v.vector(1,1,0),
    )
    ball = v.simple_sphere(
        size = v.vector(2,2,2),
        pos = v.vector(2,h,2),
        axis = v.vector(1,0,0),
        color = v.vector(0.8,0.8,0)
    )
    flak = v.compound([body, ball])
    x = random.uniform(-Game.world +1, Game.world -1)
    z = random.uniform(-Game.world +1, Game.world -1)
    y = f(x,z) * Game.max_depth
    flak.pos = v.vector(x, y + h/2, z)
    flak.hitpoints = 100
    flak.rot_speed_y = 30
    flak.rot_speed_x = 20

    Game.target_list.append(flak)
    create_flak_barrel(flak)

def create_flak_barrel(flak):
    barrel = v.cylinder( pos=v.vector(0,0,0),
                    radius = 0.2,
                    axis = v.vector(3,0,0),
                    color = v.vector(0.1,0.1,0.1)
                    )
    barrel.pos = v.vector(flak.pos.x, flak.pos.y + flak.size.y/2 -0.5, flak.pos.z)
    barrel.age = 0
    barrel.block_gun_until = 0
    barrel.move = v.vector(0,0,0) # important for bullets!
    barrel.flak = flak
    Game.flak_barrel_list.append(barrel)

def create_player():
    # ----- player (plane) -----
    body = v.box(
                    # x  y   z
        size=v.vector(2,0.25,0.25),
        pos = v.vector(0,0,0),
        color=v.vector(0.72,0.42,0)
    )
    upperwing = v.box(
                    #  x   y  z
        size=v.vector(0.5,0.05,2),
        pos = v.vector(0.5,0.2,0),
        color=v.vector(0.26,0.99,0.78),
    )
    lowerwing = v.box(
                    #  x   y  z
        size=v.vector(0.5,0.05,2),
        pos = v.vector(0.5,-0.2,0),
        color=v.vector(0.26,0.99,0.78)
    )
        #make_trail=True,
        #trail_type="points",
        #interval=10,
        #retain=150,
        #trail_color=v.vector(0,1,0)
    #)
    # back wing
    rudder1 = v.box(
        size=v.vector(0.2, 0.05, 1),
        pos=v.vector(-1, 0, 0),
        color=v.vector(0.26, 0.99, 0.78),
    )
    # rudder
    rudder2 = v.box(
                     #  x   y   z
        size=v.vector(0.2, 0.5, 0.05),
        pos=v.vector(-1, 0.25, 0),
        color=v.vector(0.26, 0.99, 0.78),
    )
    player = v.compound([body, upperwing, lowerwing, rudder1, rudder2],)
               #make_trail=True,
               #trail_type="points",
               #interval=10,
               #retain=150,
               #trail_color=v.vector(0,1,0))
    player.axis = v.vector(1, 0, 0)
    player.pos = v.vector(0, 2, 0)
    player.pos_old = v.vector(0, 2, 0)
    player.power = 0.0
    player.block_gun_until = 0.0
    player.block_bomb_until = 0.0
    player.block_rocket_until = 0.0
    player.age = 0.0
    player.move = v.vector(0,0,0)
    player.points = 0 #https://vpython.org/
    player.hitpoints = 100
    player.modus = "ground"
    player.pos.y = player.size.y // 2
    player.move = v.vector(0, 0, 0)
    player.motor = v.vector(0, 0, 0)
    player.lift = v.vector(0, 0, 0)
    player.gravity = v.vector(0, -1, 0) * Game.mass_player * Game.g
    player.ring = v.vector(0,0,0)

    player.shadow_body = v.box(pos=v.vector(0,0,0), size=v.vector(2,0,0.25), axis=v.vector(1,0,0), color=v.vector(0.2,0,0), opacity=0.5)
    player.shadow_wing = v.box(pos=v.vector(0.5,0,0), size=v.vector(5,0,0.25), axis=v.vector(1,0,0), color=v.vector(0.2,0,0), opacity=0.5)
    player.shadow_wing.rotate(angle=v.radians(90), axis=v.vector(0,1,0))
    return player

def f(x, z):
    """returns y value for a given x and z"""
    # ----- landing strip ------
    if -15 < x < 30:
        if -15 < z < 15:
            return 0
    # ---- outside world -----
    if x < -Game.world or x > Game.world or z < - Game.world or z > Game.world:
        return 1
    # ----- rest of the world ------
    t = 0.1
    return 0.7 + 0.5 * v.sin(.1 * x) * v.cos(0.1 * z) * v.sin(5 * t)

# static objects
def create_world():
    """puts diverse objects into static_list"""
    # fence post
    middle = 0
    h = Game.max_depth * 2
    Game.static_list.append(v.box(pos=v.vector(-Game.world, middle, -Game.world), size=v.vector(1.5,h,1.5)))
    Game.static_list.append(v.box(pos=v.vector(-Game.world, middle, Game.world),size=v.vector(1.5,h,1.5)))
    Game.static_list.append(v.box(pos=v.vector(Game.world, middle, -Game.world),size=v.vector(1.5,h,1.5)))
    Game.static_list.append(v.box(pos=v.vector(Game.world, middle, Game.world),size=v.vector(1.5,h,1.5)))
    # fence
    Game.static_list.append(v.cylinder(pos=v.vector(-Game.world,1,Game.world), size=v.vector(2*Game.world,0.1,0.1), color=v.vector(0,1,0)))
    Game.static_list.append(v.cylinder(pos=v.vector(-Game.world,1,-Game.world), size=v.vector(2*Game.world,0.1,0.1), color=v.vector(0,1,0)))
    Game.static_list.append(v.cylinder(pos=v.vector(-Game.world,1,Game.world), size=v.vector(2*Game.world,0.1,0.1), axis=v.vector(0,0,-1), color=v.vector(0,1,0)))
    Game.static_list.append(v.cylinder(pos=v.vector(Game.world,1,Game.world), size=v.vector(2*Game.world,0.1,0.1), axis=v.vector(0,0,-1), color=v.vector(0,1,0)))
    # ground texture
    #Game.static_list.append(v.box(
    #     pos=v.vector(0,-0.01,0),
    #     size=v.vector(Game.world*2,0.01,Game.world*2),
    #     color=v.vector(0.8,0.3,0.0),
    #     texture=v.textures.stucco,
    #     opacity = 0.2,
    #     ))
    Game.vlist = []
    parts = 10
    #Game.max_depth = -10
    for z in v.arange(-Game.world, Game.world+1,Game.world/parts ):
        li = []
        for x in v.arange(-Game.world, Game.world+1,Game.world/parts ):
            #y= random.uniform(max_depth,0)
            y = f(x,z)  * Game.max_depth
            li.append(v.vertex(pos=v.vec(x, y, z),
                               color=v.vector(0,y/Game.max_depth,0),
                               normal=v.vec(0,1,0)
                               ))
            # visible dot for each vertex
            #v.box(pos=v.vector(x,y,z),
            #      size=v.vector(0.2,0.2,0.2),
            #      color=v.vector(0.5,0.5,0.5),
            #      )
            #v.arrow(pos=v.vector(x,0,z),
            #        axis=v.vector(0,y,0),
            #        shaftwidth=1)
        Game.vlist.append(li)

    for z in range(parts*2):
        for x in range(parts*2):
            Game.static_list.append(
                v.quad(v0 = Game.vlist[z][x],
                       v1 = Game.vlist[z][x+1],
                       v2 = Game.vlist[z+1][x+1],
                       v3 = Game.vlist[z+1][x],
                       )
            )

    #Game.static_list.append(
    #    v.quad(
    #        v0=v.vertex(pos=v.vec(-Game.world, 0, -Game.world)),
    #        v1=v.vertex(pos=v.vec(-Game.world, 12.2,  Game.world)),
    #        v2=v.vertex(pos=v.vec(Game.world, -5, Game.world)),
    #        v3=v.vertex(pos=v.vec(Game.world, 4, -Game.world)),
    #        texture=v.textures.stucco,
    #             ),
    #
    #    )

    # rings to fly through
    for _ in range(5):
        Game.ring_list.append(create_ring())
    update_rings()
    Game.static_list.append(create_sun())
    #Game.static_list.append(create_cross())
    for _ in range(4):
        create_building()
    for _ in range(5):
        create_flak()
    #for _ in range(14):
     #   create_tank()
    #for t in Game.tank_list:
    #    v.attach_arrow(t, "up", color=v.vector(1,1,1))

def update_hud():
    Game.hud.text = f"score: {Game.player1.points} hp: {Game.player1.hitpoints} engine: {(Game.player1.power/Game.max_power)*100:.0f}% mode: {Game.player1.modus} y: {Game.player1.pos.y:.1f} ground:{f(Game.player1.pos.x, Game.player1.pos.z)*Game.max_depth:.1f} hog: {Game.player1.pos.y - f(Game.player1.pos.x, Game.player1.pos.z)*Game.max_depth:.1f} distance to next ring: {v.mag(Game.ring_distance):.2f} "

def create_particle(pos, color=None):
    if color is None:
        color = v.vector(random.random(), random.random(), random.random())
    size = random.random() * 0.1 + 0.01
    p = v.box(pos=pos, size=v.vector(size,size,size), color=color, axis=v.vector.random())
    p.max_age = random.random() + 0.1
    p.age = 0
    p.move = v.vector.random()
    p.move *= 10
    Game.particle_list.append(p)


def rotate_plane(player):
    """rotate smoke emitters at the plane's wings """
    pos1 = v.vector(player.pos.x, player.pos.y, player.pos.z)
    # pos=v.vector(0.7,0,1),
    pos1 += player.axis.norm() * 0.7
    pos2 = pos1 + v.cross(player.axis, player.up)
    pos3 = pos1 - v.cross(player.axis, player.up)
    return pos2, pos3

def fly():
    ground_here = f(Game.player1.pos.x, Game.player1.pos.z) * Game.max_depth
    if (Game.player1.pos.y -  Game.radius_player) >= ground_here:
        Game.player1.modus = "fly"
        Game.player1.gravity = v.vector(0, -1, 0) * Game.g * Game.mass_player * Game.dt
        if (Game.player1.pos.y - ground_here) < (2 * Game.radius_player):
            for _ in range(5):
                create_particle(Game.player1.pos , color=v.vector(0.1, 0.1, 0.1))
    elif (Game.player1.pos.y - Game.radius_player) < ground_here:
        # dirt particles
        Game.player1.pos.y = ground_here + Game.radius_player
        Game.player1.gravity = v.vector(0, 0, 0)
        # Game.player1.gravity = v.vector(0,0,0)
        if Game.player1.axis.y < 0:
            Game.player1.power = 0 # turn engine off
        #    if Game.player1.modus == "fly":
        #        for _ in range(50):
        #            print("particle!")
        #            create_particle(Game.player1.pos + v.vector(0, 2, 0), color=v.vector(0.1, 0.1, 0.1))
        Game.player1.modus = "ground"
    #else:
    #    Game.player1.modus = "ground"
    #if Game.player1.modus == "ground":

    Game.player1.motor = Game.player1.power * Game.dt * Game.player1.axis.norm()
    # gravitation
    # gravity = 9.81 * dt * v.vector(0,-1,0) #player1.up.norm()  # v.vector(0,-1,0) # player1.up.norm()  #TODO ABSOLUTE GRAVITY

    # -------- lift ------
    # a = nose of the plane
    # b = moving the plane
    # print("comp b.a", b.axis.comp(a.axis))
    # p = v.arrow(pos=v.vector(0, 0, 0), axis=v.proj(b.axis, a.axis), shaftwidth=0.1, color=v.vector(0.5, 0, 0.5))
    #Game.player1.lift = Game.lift_factor * Game.player1.power * Game.dt * Game.player1.up.norm()
    if Game.player1.move.comp(Game.player1.axis) > 0:
        # Auftrieb findet statt
        Game.player1.lift = v.mag(v.proj(Game.player1.move, Game.player1.axis)) * Game.player1.up.norm() * Game.dt * Game.lift_factor
    else:
        # stall
        Game.player1.lift = v.vector(0,0,0)

    Game.player1.move += Game.player1.motor + Game.player1.lift
    # drag
    drag = Game.player1.move.mag2 * Game.drag_player * -Game.player1.move.norm()
    Game.player1.move += drag

    # flugzeug position update
    #position_old = v.vector(player1.pos.x, player1.pos.y, player1.pos.z)
    Game.player1.pos_old = v.vector(Game.player1.pos.x, Game.player1.pos.y, Game.player1.pos.z)
    Game.player1.pos += Game.player1.move
    #if player1.pos.y < 0 and position_old.y >= 0:
    #    player1.power = 0
    # positionslichter update
    Game.smoke1.pos += Game.player1.move
    Game.smoke2.pos += Game.player1.move

    #if Game.player1.pos.y < Game.player1.size.y / 2:
    #    Game.player1.pos.y = Game.player1.size.y / 2
    #    Game.smoke1.pos.y = Game.player1.size.y / 2
    #    Game.smoke2.pos.y = Game.player1.size.y / 2

    #elif Game.player1.pos.y >= Game.player1.size.y / 2:
    if Game.player1.modus == "fly":
        Game.player1.move += Game.player1.gravity

    # update camera axis
    #Game.scene1.forward = Game.player1.axis
    # update shadow
    hog = v.vector(Game.player1.pos.x, f(Game.player1.pos.x, Game.player1.pos.z) * Game.max_depth, Game.player1.pos.z)
    #hog_old = v.vector(Game.player1.pos_old.x, f(Game.player1.pos_old.x, Game.player1.pos_old.z) * Game.max_depth, Game.player1.pos_old.z)
    #diff = hog - hog_old
    Game.player1.shadow_body.axis = v.vector(Game.player1.axis.x, 0 , Game.player1.axis.z)
    Game.player1.shadow_wing.axis = v.vector(Game.player1.axis.x, 0, Game.player1.axis.z).rotate(angle=v.radians(90), axis=Game.player1.shadow_wing.up)

    Game.player1.shadow_body.pos = v.vector(Game.player1.pos.x, hog.y+1, Game.player1.pos.z)
    Game.player1.shadow_wing.pos = Game.player1.pos + v.norm(Game.player1.axis) * 0.25
    Game.player1.shadow_wing.pos.y = hog.y + 1
    #Game.player1.shadow_body.axis.y = diff.y
    #Game.player1.shadow_wing.axis.y = diff.y


def update_rockets():
    for rocket in Game.rocket_list:
        #if rocket.fresh:
        #    rocket.move += (v.norm(rocket.axis) + v.vector.random() * rocket.error) * Game.dt
        #    rocket.fresh = False
        #rocket.move += Game.g * Game.mass_rocket * v.vector(0,-1,0) * Game.dt
        if rocket.age < Game.rocket_fuel:
            rocket.move += v.norm(rocket.axis) * Game.rocket_power  * Game.dt
            create_explosion(pos=rocket.pos, max_age=0.2, color=v.vector(1,1,1))
        rocket.pos += rocket.move
        rocket.age += Game.dt



        ground_here = f(rocket.pos.x, rocket.pos.z) * Game.max_depth
        if rocket.pos.y <= ground_here or rocket.age > rocket.max_age:
            create_explosion(pos=rocket.pos, max_age=1.2, color=v.vector(.8, .1, .1) )
            rocket.visible = False
            rocket.delete()

    Game.rocket_list = [r for r in Game.rocket_list if r.visible]


def update_bullets():
    for bullet in Game.bullet_list:
        if bullet.fresh:
            bullet.move += (v.norm(bullet.axis) + v.vector.random() * bullet.error) * Game.cannon_power * Game.dt
            bullet.fresh = False
        bullet.move += Game.g * Game.mass_bullet  * v.vector(0,-1,0)
        # drag = bullet.move.mag2 * 5.515 * -bullet.move.norm()
        #bullet.move += drag
        bullet.pos += bullet.move * Game.dt
        bullet.age += Game.dt
        # collision detection bullet <-> target
        if bullet.shooter == Game.player1:
            for target in Game.target_list:
                distance = bullet.pos - target.pos
                if abs(distance.x) < target.size.x / 2:
                    if abs(distance.y) < target.size.y / 2:
                        if abs(distance.z) < target.size.z / 2:
                            # explosion
                            create_explosion(pos=bullet.pos, hit=True)
                            Game.player1.points += 1
                            # hud.text = f"points: {player1.points} engine power: {player1.power:.2f}"
                            # update_hud()
                            target.hitpoints -= 2  # damage of bullet
                            #bullet.age = bullet.max_age
                            bullet.visible = False
                            bullet.delete()

        else:
            # ---- flak bullet, target is the player ! -----
            target = Game.player1
            distance = bullet.pos - target.pos
            if v.mag(distance) < Game.flak_crit_distance:
                target.hitpoints -= 1
                create_explosion(bullet.pos, hit=False)
                #bullet.age = bullet.max_age
                bullet.visible = False
                bullet.delete()

        ground_here = f(bullet.pos.x, bullet.pos.z) * Game.max_depth
        if bullet.pos.y <= ground_here:
            # bullet.age = 1+ bullet.max_age
            create_explosion(pos=bullet.pos)
            #bullet.age = bullet.max_age
            bullet.visible = False
            bullet.delete()
        if bullet.age > bullet.max_age:
            bullet.visible = False
            bullet.delete()
    Game.bullet_list = [b for b in Game.bullet_list if b.visible]

def update_rings():
    for index, r in enumerate(Game.ring_list):
        if index == Game.ring_index:
            r.color = v.vector(0,0,1) # blue
        else:
            r.color = v.vector(1,1,1) # white

def update_flak_barrels():
    for b in Game.flak_barrel_list:
        b.age += Game.dt
        distance = Game.player1.pos - b.pos
        b.axis = v.norm(distance) * 3
        if b.flak.hitpoints > 0 and v.mag(distance) < Game.flak_range and b.age > b.block_gun_until:
            create_bullet()

def update_bombs():
    for b in Game.bomb_list:
        gravity = Game.g * Game.mass_bomb * v.vector(0,-1,0)
        #print("b.move", b.move, "move:", move)
        b.move += gravity
        #b.move += 0.0181 * dt * v.vector(0, -1, 0).norm()
        b.pos += b.move * Game.dt
        # --- collision detection bomb -> target --
        for target in Game.target_list:
            distance = b.pos - target.pos
            if abs(distance.x) < target.size.x / 2:
                if abs(distance.y) < target.size.y / 2:
                    if abs(distance.z) < target.size.z / 2:
                        # explosion
                        create_explosion(pos=b.pos, hit=True, max_age=7)
                        Game.player1.points += 1
                        # hud.text = f"points: {player1.points} engine power: {player1.power:.2f}"
                        # update_hud()
                        target.hitpoints -= 10
                        # b.age = b.max_age  # AUSKOMMENTIEREN!
                        b.visible = False
                        b.delete()
        ground_here = f(b.pos.x, b.pos.z) * Game.max_depth
        if b.pos.y < ground_here:
            b.visible = False
            b.delete()
            create_explosion(b.pos)
            #explosion_list.append(create_flash)
    Game.bomb_list = [b for b in Game.bomb_list if  b.visible]

def update_explosions():
    # explosion animation
    for e in Game.explosion_list:
        e.age += Game.dt
        e.radius = 0.01 + e.age * 1.1
        if e.hit:
            red, green, blue = e.color.x, e.color.y, 0
        else:
            red, green, blue = e.color.x, e.color.y, e.color.z
        if e.age < e.max_age:
            red += random.uniform(-0.2, 0.2)
            red = min(1, red)
            red = max(0, red)
            green += random.uniform(-0.2, 0.2)
            green = min(1, green)
            green = max(0, green)
            blue += random.uniform(-0.2, 0.2)
            blue = min(1, blue)
            blue = max(0, blue)
            e.color = v.vector(red, green, blue)
        else:
            e.visible = False
            e.delete()
    Game.explosion_list = [e for e in Game.explosion_list if e.visible]

def update_particles():
    # particle movement
    for p in Game.particle_list:
        p.age += Game.dt
        p.move += Game.g * Game.mass_particle * v.vector(0,-1,0)
        p.pos += p.move * Game.dt
        if p.pos.y < 0:
            p.age = p.max_age
        if p.age >= p.max_age:
            p.visible = False
            p.delete()
    Game.particle_list = [p for p in Game.particle_list if p.visible]

def update_tanks():
    # tank movement
    for t in Game.tank_list:
        if t.hitpoints > 0:
            old_pos = v.vector(t.pos.x, t.pos.y, t.pos.z)
            t.pos += t.move * Game.dt
            bounce = False
            if t.pos.x < -Game.world:
                t.pos.x = -Game.world
                bounce = True
                new_angle = -t.angle + 180  # bounce direction
                t.rotate(angle=v.radians(new_angle - t.angle), axis=t.up)
                t.move = t.axis.norm() * t.power
                t.angle = new_angle
                #t.move = v.vector(random.randint(1,20),0,random.randint(-50, 50)).norm() * t.power
                #t.axis = t.move.norm()
            if t.pos.x > Game.world:
                t.pos.x = Game.world
                bounce = True
                new_angle = -t.angle + 180  # bounce direction
                t.rotate(angle=v.radians(new_angle - t.angle), axis=t.up)
                t.move = t.axis.norm() * t.power
                t.angle = new_angle
            if t.pos.z < -Game.world:
                t.pos.z = -Game.world
                bounce = True

                new_angle = -t.angle  # bounce direction
                t.rotate(angle=v.radians(new_angle - t.angle), axis=t.up)
                t.move = t.axis.norm() * t.power
                t.angle = new_angle

            if t.pos.z > Game.world:
                t.pos.z = Game.world
                bounce = True

                new_angle = -t.angle  # bounce direction
                t.rotate(angle=v.radians(new_angle - t.angle), axis=t.up)
                t.move = t.axis.norm() * t.power
                t.angle = new_angle



            # ----- over ground ------
            ground_here = f(t.pos.x, t.pos.z) * Game.max_depth
            #t.hy.y  = ground_here
            t.pos.y = ground_here + t.size.y / 2
            # update tank axis
            if not bounce:
                t.axis = t.pos - old_pos

    #return tank_list

def slider_dt(s):
    Game.dt = s.value
    Game.label_dt.text = f"{Game.dt:.4f}"

def slider_lift(s):
    Game.lift_factor = s.value
    Game.label_lift.text = f"{Game.lift_factor:.4f}"

def slider_ring_center_distance(s):
    """how close the player must fly to the center of a ring to proceed to next ring"""
    Game.ring_center_distance = s.value
    Game.label_ring_center_distance.text = f"{Game.ring_center_distance:.1f}"

def slider_rotation(s):
    """how fast the plane rotates around its axis"""
    Game.rotation = s.value
    Game.label_rotation.text = f"{Game.rotation:.1f}"

def slider_delay(s):
    """time delay of the camera flying behind the player """
    Game.camera_delay = s.value
    Game.label_delay.text = f"{Game.camera_delay:.2f}"

def create_widgets():
    Game.scene1.append_to_title(" keys: engine: 1=full 2=more 3=less 4=off. flight controls: WASDQE gun: Space bomb: Ctrl")
    Game.scene1.append_to_title(" or use first joystick")
    Game.scene1.append_to_caption("rotation speed: ")
    v.slider(bind=slider_rotation, min=1, max=200, step=0.1, value=Game.rotation)
    Game.label_rotation = v.wtext(text=f"{Game.rotation}")
    Game.scene1.append_to_caption(Game.label_rotation)
    Game.scene1.append_to_caption('\n\n')
    Game.scene1.append_to_caption("camera delay [seconds]:")
    v.slider(bind=slider_delay, min=0, max=5, step=0.01, value=Game.camera_delay)
    Game.label_delay = v.wtext(text=f"{Game.camera_delay:.2f}")
    Game.scene1.append_to_caption(Game.label_delay)
    Game.scene1.append_to_caption('\n\n')
    Game.scene1.append_to_caption("ring_center_distance:")
    v.slider(bind= slider_ring_center_distance, min=0.2, max=15.0, step=0.1, value=Game.ring_center_distance)
    Game.label_ring_center_distance = v.wtext(text=f"{Game.ring_center_distance:.1f}")
    Game.scene1.append_to_caption(Game.label_ring_center_distance)
    Game.scene1.append_to_caption('\n\n')
    Game.scene1.append_to_caption("dt (delta time) in [seconds]:")
    v.slider(bind=slider_dt, min=0.0001, max=0.01, step=0.00001, value=Game.dt)
    Game.label_dt = v.wtext(text=f"{Game.dt:.4f}")
    Game.scene1.append_to_caption(Game.label_dt)
    Game.scene1.append_to_caption('\n\n')
    Game.scene1.append_to_caption("lift_factor (force up vs. force forward):")
    v.slider(bind=slider_lift, min=0.0, max=200.0, step=0.1, value=Game.lift_factor)
    Game.label_lift = v.wtext(text=f"{Game.lift_factor:.4f}")
    Game.scene1.append_to_caption(Game.label_lift)
    Game.scene1.append_to_caption('\n\n')

def main():
    # Initialize the joysticks.
    pygame.init()
    joystick_count = pygame.joystick.get_count()
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
    #joystick = pygame.joystick.Joystick(0)
    #joystick.init()

    create_widgets()

    # horst spielt mit Camera
    Game.scene1.center= v.vector(0,0,0)
    #scene1.autoscale=False
    Game.scene1.camera.pos = v.vector(0,0,-1)
    Game.player1 = create_player()
    #Game.scene1.camera.follow(Game.player1)

    Game.hud = v.label(pixel_pos=True,
                          pos=v.vec(5,15,0),
                          text=f"points: {Game.player1.points}",
    #hud.text = f"points: {player1.points} engine power: {player1.power:.2f}"
                          color=v.vector(1,1,0),
                          align="left",
                          opacity=0,
                          box=False,
                          )

    Game.smoke1 = v.simple_sphere(pos=v.vector(0.7,0,1),
                   size=v.vector(0.25,0.25,0.25),
                   color=v.vector(0,1,0), # rechts grün   )
                   make_trail=True,
                   trail_type="points",
                   interval=15,
                   retain=50,
                   trail_color=v.vector(0,1,0),
                   )
    Game.smoke2 = v.simple_sphere(pos=v.vector(0.7,0,-1),
                   size=v.vector(0.25,0.25,0.25),
                   color=v.vector(1,0,0), # links rot)
                   make_trail=True,
                   trail_type="points",
                   interval=15,
                   retain=50,
                   trail_color=v.vector(1,0,0),
    )
    create_world() # put stuff into static_list
    # -------------- movement -------------
    #age = 0
    Game.ring_index = 0
    Game.my_ring = Game.ring_list[Game.ring_index]
    Game.disc= v.cylinder(pos=Game.my_ring.pos, axis=Game.my_ring.axis, radius=Game.ring_center_distance/2, length=0.1, color=v.vector(1,0,0))
    Game.ring_distance = Game.player1.pos - Game.my_ring.pos

    a7 = v.attach_arrow(Game.player1, "ring", scale=55, shaftwidth=0.2, color=v.color.blue)
    #a8 = v.attach_arrow(Game.player1, "axis", scale=100, color=v.color.white)
    camera_zoom = 1.0
    camera_x_angle = 0.0
    camera_y_angle = 0.0
    camera_change = False

    while True:
        v.rate(200)
        #age += Game.dt
        #gravity = v.vector(0, -1, 0) * Game.g_player * Game.dt
        Game.player1.age += Game.dt

        # player movement
        # player1.pos += player1.power * dt * player1.axis.norm()
        fly() # player1
        # ------update camera ---
        # this is the same as follow player1
        #Game.scene1.camera.pos = Game.player1.pos + v.norm(
        #    v.vector(Game.player1.axis.x, Game.player1.axis.y, Game.player1.axis.z)) * -9 + v.vector(0, 5, 0)
        ray = v.norm(Game.player1.axis) * 10

        new_pos = Game.player1.pos - ray + v.vector(0,5,0)
        f_value = f(new_pos.x, new_pos.z) * Game.max_depth
        height_over_ground = new_pos.y - f_value
        if height_over_ground < 5:
            new_pos.y += 5 - height_over_ground

        Game.scene1.camera.pos = new_pos
        Game.camera_history.append(new_pos)
        Game.scene1.camera.pos = Game.camera_history[0]
        while len(Game.camera_history) > Game.camera_delay / Game.dt:
            Game.scene1.camera.pos = Game.camera_history.pop(0)
        caxis = v.norm(Game.player1.pos - Game.scene1.camera.pos) * 10
        if camera_x_angle != 0:
            caxis = v.rotate(caxis, angle=v.radians(camera_x_angle), axis=v.vector(0,1,0))
        # ---- too confusing for the human eye ----
        #if camera_y_angle != 0:
        #    caxis = v.rotate(caxis, angle=v.radians(camera_y_angle), axis=v.vector(v.cross(caxis, v.vector(0,1,0))))


        Game.scene1.camera.pos = Game.player1.pos - caxis
        Game.scene1.camera.axis = caxis
        #Game.scene1.camera.pos = new_pos
        #Game.scene1.camera.axis = v.norm(Game.player1.pos - Game.scene1.camera.pos) * 10

        # ---- ring control -----

        Game.ring_distance = Game.player1.pos - Game.my_ring.pos
        if v.mag(Game.ring_distance) < Game.ring_center_distance:
            if Game.ring_index == len(Game.ring_list) - 1:
                Game.ring_index = 0
            else:
                Game.ring_index += 1
            Game.my_ring = Game.ring_list[Game.ring_index]
            Game.disc.visible = False
            Game.disc.delete()
            Game.disc = v.cylinder(pos=Game.my_ring.pos, axis=Game.my_ring.axis, radius=0.5, length=0.1, color=v.vector(1,0,0))
            update_rings()
            Game.player1.points += 100
            # confetti for player
            for _ in range(100):
                create_particle(Game.player1.pos)
        rdiff = Game.my_ring.pos - Game.player1.pos
        Game.player1.ring = v.norm(rdiff) * 0.05
        #print(rdiff, v.mag(rdiff), v.norm(rdiff), v.mag(v.norm(rdiff)))
        #Game.player1.ring = v.norm(Game.ring_list[Game.ring_index].pos - Game.player1.pos) * 3
        update_hud()
        # --- event handler
        # k = keysdown()  # a list of keys that are down
        keys = v.keysdown()
        for char in "wasdqe,.":
            if char in keys:
                if ('a' in keys or "," in keys) and not ('d' in keys or "." in keys):
                    Game.player1.rotate(angle=v.radians(Game.rotation) * Game.dt, axis=Game.player1.up)
                    # smoke1.axis, smoke2.axis = player1.axis.norm()*0.1, player1.axis.norm()*0.1
                if ('d' in keys or "." in keys) and not ('a' in keys or "," in keys):
                    Game.player1.rotate(angle=v.radians(-Game.rotation) * Game.dt, axis=Game.player1.up)
                if "s" in keys and not "w" in keys:
                    Game.player1.rotate(angle=v.radians(Game.rotation) * Game.dt,
                                        axis=v.cross(Game.player1.axis, Game.player1.up))
                if "w" in keys and not "s" in keys:
                    Game.player1.rotate(angle=v.radians(-Game.rotation) * Game.dt,
                                        axis=v.cross(Game.player1.axis, Game.player1.up))
                if "e" in keys and not "q" in keys:
                    Game.player1.rotate(angle=v.radians(Game.rotation) * Game.dt,
                                        axis=Game.player1.axis)  # axis=v.vector(1, 0, 0), )
                if "q" in keys and not "e" in keys:
                    Game.player1.rotate(angle=v.radians(-Game.rotation) * Game.dt,
                                        axis=Game.player1.axis)  # axis=v.vector(1, 0, 0), )
                # whatever rotation, update the somke emitters:
                Game.smoke1.pos, Game.smoke2.pos = rotate_plane(Game.player1)
            #smoke1.axis, smoke2.axis = player1.axis.norm() * 0.1, player1.axis.norm() * 0.1
        #if "p" in keys:
        #    create_particle(Game.player1.pos)
        # ---- update sprites ----
        update_bullets()
        update_bombs()
        update_rockets()
        update_explosions()
        update_particles()
        update_tanks()
        update_flak_barrels()
        # ---------- joystick ---------
        # see joystick module in pygame documentation
        # ------ necessary! without pygame event.get(), joystick events are not pulled ----
        for event in pygame.event.get():  # User did something.
            if event.type == pygame.QUIT:  # If user clicked close.
                pass # done = True  # Flag that we are done so we exit this loop.
            #elif event.type == pygame.JOYBUTTONDOWN:
            #    print("Joystick button pressed.")
            #elif event.type == pygame.JOYBUTTONUP:
            #    print("Joystick button released.")
        if joystick_count > 0:
            joystick = pygame.joystick.Joystick(0)
        else:
            joystick = None
        if " " in keys or (joystick is not None and joystick.get_button(5)):
            # ---------fire forward gun ----------
            if Game.player1.age > Game.player1.block_gun_until:
                create_bullet(shooter=Game.player1, )

        if "ctrl" in keys or (joystick is not None and joystick.get_button(4)):
            # -------- drop bomb --------------
            #if Game.player1.age > Game.player1.block_bomb_until:
            #    create_bomb(shooter=Game.player1)
            if Game.player1.age > Game.player1.block_rocket_until:
                create_rocket()

        if "1" in keys or (joystick is not None and joystick.get_button(0)):
            print("1 pressed")
            Game.player1.power = Game.max_power
        elif "2" in keys or (joystick is not None and joystick.get_axis(3) < -0.1):
            Game.player1.power += 0.01
            Game.player1.power = min(Game.max_power, Game.player1.power)
        elif "3" in keys or (joystick is not None and joystick.get_axis(3) > 0.1):
            Game.player1.power -= 0.01
            Game.player1.power = max(Game.min_power, Game.player1.power)
        elif "4" in keys:
            Game.player1.power = 0
        if "c" in keys or (joystick and joystick.get_button(1)):
            # --- reset camera ---
            camera_zoom = 1.0
            camera_x_angle = 0.0
            camera_y_angle = 0.0

        if joystick is not None:
            # flight control
            if joystick.get_axis(0) != 0 or joystick.get_axis(1) != 0 or joystick.get_axis(4) != 0:
                # get_axis(<number of axis>) is a float value from -1 to +1, 0 at neutral position
               # if joystick.get_axis(0) != 0:
                    # --------- joystick rudder (yaw) left/right ----------------
                 #   Game.player1.rotate(angle=v.radians(Game.rotation * -joystick.get_axis(0)) * Game.dt,
                        #                axis=Game.player1.up)

                #peter - emile
                if joystick.get_axis(2) != -1 or joystick.get_axis(5) != -1:
                    diff = (1 + joystick.get_axis(2)) - (1 + joystick.get_axis(5))
                    print("diff:", diff)
                    Game.player1.rotate(angle=v.radians(Game.rotation * diff * 0.5) * Game.dt, axis=Game.player1.up)


                if joystick.get_axis(1) != 0:
                    # -------- joystick roll left/right -------------------
                    Game.player1.rotate(angle=v.radians(Game.rotation * joystick.get_axis(1)) * Game.dt,
                                        axis=Game.player1.axis)  # axis=v.vector(1, 0, 0), )
                if joystick.get_axis(4) != 0:
                    # -------- joystick pitch up/down -------------------
                    # get_axis(3) is a float value from -1 to +1, 0 at neutral position
                    Game.player1.rotate(angle=v.radians(Game.rotation * joystick.get_axis(4)) * Game.dt,
                                        axis=v.cross(Game.player1.axis, Game.player1.up))
                # in any rotation event, update the smoke emitters position:
                Game.smoke1.pos, Game.smoke2.pos = rotate_plane(Game.player1)
            # camera control
            if joystick.get_hat(0)[0] == -1:
                camera_x_angle -= 0.25
                camera_change = True
            elif joystick.get_hat(0)[0] == 1:
                camera_x_angle += 0.25
                camera_change = True


if __name__ == "__main__":
    main()



