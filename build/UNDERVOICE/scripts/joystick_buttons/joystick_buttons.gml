/// @func	joystick_buttons(id)
/// @desc	(Legacy GM) Returns the number of buttons the joystick has.
/// @param	{real}	id	The id of the joystick (1 or 2).
/// @return	{real}	The number of buttons the joystick has.
function joystick_buttons(_id)
{
	var jid = __joystick_2_gamepad(_id)
	return gamepad_button_count(jid);
}
