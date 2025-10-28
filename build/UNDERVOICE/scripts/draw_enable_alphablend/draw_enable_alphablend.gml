/// @func	draw_enable_alphablend(val)
/// @desc	(Legacy GM) Toggles alpha blending on or off.
/// @param	{bool}	val	This can be either true (switched on) or false (switched off)
function draw_enable_alphablend(_val)
{
	gpu_set_blendenable(_val)
}
