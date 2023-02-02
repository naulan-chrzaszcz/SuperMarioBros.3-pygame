from fr.naulan.maps_creator.src.ui.buttons.action.button_action import ButtonAction


class ChangeColorButtonAction(ButtonAction):
    def action(self, *args, **kwargs):
        self.button.color_background = (0, 0, 0)
