from fr.naulan.maps_creator.src.ui.observer import Observer


class OnClickObserver(Observer):

    def update(self, observable_object):
        if observable_object.clicked:
            print("Je suis clické")
