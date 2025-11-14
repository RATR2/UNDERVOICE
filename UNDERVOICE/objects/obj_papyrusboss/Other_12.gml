global.myfight = 19
instance_create(0, 0, obj_unfader)
if (!global.fakefight){
    FL_PapyrusStatus = PapyrusStatus.Spared
    if (killed == 1)
	   FL_PapyrusStatus = PapyrusStatus.Killed   
    global.plot = 100
}
alarm[9] = 45
caster_free(all)
