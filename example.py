from ps2_controller import PS2_Controller
from time import sleep_ms

PS2_DATA = 19
PS2_CMD  = 23
PS2_ATT  = 5
PS2_CLK  = 18

controller = PS2_Controller( PS2_DATA, PS2_CMD, PS2_ATT, PS2_CLK )

middle_pos = ( 127, 128 )
while True:
    keys = controller.read_keys()
    
    if len(keys) > 5 or any(k not in middle_pos for k in keys[1:5]):
        print(keys)
    sleep_ms(20)