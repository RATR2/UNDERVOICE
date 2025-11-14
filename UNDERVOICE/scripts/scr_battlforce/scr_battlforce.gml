function scr_battlforce(whom) { 
    if (instance_exists(obj_battlecontroller)) { 
        show_debug_message("already in fight"); 
        return;
    }
    if (room == room_intromenu) {
        show_debug_message("in menu")
        return;
    }
	with (obj_savepoint)
		instance_destroy()
	with (OBJ_WRITER)
		instance_destroy()
	with (obj_dialoguer)
		instance_destroy()
    switch (whom) {
        case "undyne":
            global.battlegroup = BattleGroup.Undyne
            global.fakefight = true
            global.oldmercy = global.mercy
            global.mercy = 0
			global.border = 12
            scr_save()
            break;
        case "sans":
            global.battlegroup = BattleGroup.Sans
            global.oldmercy = global.mercy
            global.mercy = 0
            global.fakefight = true
            scr_save()
            break;
        case "papyrus":
			global.battlegroup = BattleGroup.Papyrus
            global.oldmercy = global.mercy
            global.mercy = 0
            global.fakefight = true
            scr_save()
            break;
		case "asriel":
			global.battlegroup = BattleGroup.Asriel
            global.oldmercy = global.mercy
            global.mercy = 0
            global.fakefight = true
            scr_save()
            break;
		case "asgore":
			global.battlegroup = BattleGroup.AsgoreIntro
            global.oldmercy = global.mercy
            global.mercy = 0
            global.fakefight = true
            scr_save()
            break;
		case "dummy":
			global.battlegroup = BattleGroup.MadDummy
            global.oldmercy = global.mercy
            global.mercy = 0
            global.fakefight = true
            scr_save()
            break;
		case "toriel":
			global.battlegroup = BattleGroup.Toriel
            global.oldmercy = global.mercy
            global.mercy = 0
            global.fakefight = true
            scr_save()
            break;
        default:
            show_debug_message("Unknown enemy!");
            break;
    }
	instance_create(0, 0, obj_battler)
}
