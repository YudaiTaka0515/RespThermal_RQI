import cvui


inspiration3 = 'breath in  3'
inspiration2 = 'breath in  2'
inspiration1 = 'breath in  1'
inspiration0 = 'breath in  0'

exhalation3 = 'breath out 3'
exhalation2 = 'breath out 2'
exhalation1 = 'breath out 1'
exhalation0 = 'breath out 0'

inspiration_color = 0x00ffff
exhalation_color = 0xffd700


def DisplayClock(displayed_time, window_frame, p_instruction_text, dt):
    if displayed_time < dt:
        cvui.text(window_frame, p_instruction_text.x, p_instruction_text.y,
                  inspiration0, p_instruction_text.size, inspiration_color)
    elif displayed_time < dt * 2:
        cvui.text(window_frame, p_instruction_text.x, p_instruction_text.y,
                  inspiration1, p_instruction_text.size, inspiration_color)
    elif displayed_time < dt * 3:
        cvui.text(window_frame, p_instruction_text.x, p_instruction_text.y,
                  inspiration2, p_instruction_text.size, inspiration_color)
    elif displayed_time < dt * 4:
        cvui.text(window_frame, p_instruction_text.x, p_instruction_text.y,
                  inspiration3, p_instruction_text.size, inspiration_color)
    elif displayed_time < dt * 5:
        cvui.text(window_frame, p_instruction_text.x, p_instruction_text.y,
                  exhalation0, p_instruction_text.size, exhalation_color)
    elif displayed_time < dt * 6:
        cvui.text(window_frame, p_instruction_text.x, p_instruction_text.y,
                  exhalation1, p_instruction_text.size, exhalation_color)
    elif displayed_time < dt * 7:
        cvui.text(window_frame, p_instruction_text.x, p_instruction_text.y,
                  exhalation2, p_instruction_text.size, exhalation_color)
    else:
        cvui.text(window_frame, p_instruction_text.x, p_instruction_text.y,
                  exhalation3, p_instruction_text.size, exhalation_color)