import pygame

def movement_control(robot, mode="standard", decay=False, max_speed=3.0):
    keys = pygame.key.get_pressed()

    if mode == "standard":
        if keys[pygame.K_q]:
            robot.set_vl(True)
        if keys[pygame.K_a]:
            robot.set_vl(False)
        if keys[pygame.K_w]:
            robot.set_vr(True)
        if keys[pygame.K_s]:
            robot.set_vr(False)

        if not (keys[pygame.K_q] or keys[pygame.K_a]):
            robot.vl_decay += 1
        if not (keys[pygame.K_w] or keys[pygame.K_s]):
            robot.vr_decay += 1

    elif mode == "reverse":
        if keys[pygame.K_q]:
            robot.set_vr(True)
        if keys[pygame.K_a]:
            robot.set_vr(False)
        if keys[pygame.K_w]:
            robot.set_vl(True)
        if keys[pygame.K_s]:
            robot.set_vl(False)

        if not (keys[pygame.K_q] or keys[pygame.K_a]):
            robot.vr_decay += 1
        if not (keys[pygame.K_w] or keys[pygame.K_s]):
            robot.vl_decay += 1

    elif mode == "direct":
        speed = max_speed
        vl = vr = 0

        if keys[pygame.K_w]:
            vl = vr = speed
        elif keys[pygame.K_s]:
            vl = vr = -speed

        if keys[pygame.K_a]:
            vl -= 0.5 * speed
            vr += 0.5 * speed
        elif keys[pygame.K_d]:
            vl += 0.5 * speed
            vr -= 0.5 * speed

        # Clamp
        robot.vl = max(min(vl, max_speed), -max_speed)
        robot.vr = max(min(vr, max_speed), -max_speed)

    if decay and mode in ("standard", "reverse"):
        robot.apply_vl_decay()
        robot.apply_vr_decay()
