if (FL_GetDunkedOn == 0)
	caster_loop(gameoversong, 1, 1)
if (!global.fakefight){ 
    if (FL_GetDunkedOn == 1)
	   caster_loop(gameoversong, 0.9, 1.25)
} else {
    caster_loop(gameoversong, 1, 1)
}
instance_create(0, 0, obj_gameoverbg)
alarm[3] = 80
