""" This program takes an image of a blackjack playing surface and identifies the cards and chips """

### Import necessary packages ###
import os
import cv2
import copy
import imutils
import display
import argparse

### Import own libraries ###
import surface
import cards
import chips
import gesture

### Constants ###
rank_path = 'rank_images'
benchmark_img_dir = 'benchmark_images'
benchmark_res_dir = os.path.join('benchmark_images','results')
font = cv2.FONT_HERSHEY_SIMPLEX

def videoTest():
    """ Run the blackjack program on a webcam """

    # Command line input to specify the camera index to use
    parser = argparse.ArgumentParser(
        description='Blackjack tracker')
    parser.add_argument('-camera', action='store', type = int,
                        dest='cam_index',
                        default=0,
                        help='Specify the camera index (0,1,2,...)',
                        )
    args = parser.parse_args()

    # set up the camera and set max resolution
    cap = cv2.VideoCapture(args.cam_index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 9999)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 9999)

    # Set up a historical list of cards
    last_cards = []

    # Run through countdown and grab playing surface. Returns an surface
    # object.
    playing_surface = surface.get_surface(cap, 100)

    state = 0
    # If initialisation found a successful transform, else exit the program
    if playing_surface is not None:
        while (True):

            # Get the next frame
            (flag, img) = cap.read()

            # Transform using the transformation matrix found during
            # initialisation
            transformed = cv2.warpPerspective(img, playing_surface.perspective_matrix,
                                              (playing_surface.width, playing_surface.height))

            # Start in the card and chip detection state
            if state == 0:
                img_disp = copy.deepcopy(transformed)

                # Get a list of card objects in the image and draw on temp image
                all_cards = cards.detect(transformed, rank_path, last_cards)
                last_cards = copy.deepcopy(all_cards)
                img_disp = cards.display(img_disp, all_cards)

                # Find all of the chips and draw them on the temp image
                all_chips = chips.detect(transformed)
                img_disp = chips.display(img_disp, all_chips)

                # Add dealer and player regions to the displayed surface
                display.regions(img_disp, playing_surface)
                display.hand_values(img_disp, playing_surface, all_cards, state)
                display.bet(img_disp, playing_surface, all_chips)

                cv2.imshow("Blackjack Tracker", imutils.resize(img_disp, height=600))
                cv2.moveWindow("Blackjack Tracker", 0, 0)

                key = cv2.waitKey(delay=1)

                if key == ord('t'):
                    # cv2.destroyAllWindows()
                    state = not state
                elif key == ord('c'):
                    playing_surface = surface.get_surface(cap, 10)
                    # print('Recalibration failed. No successful transform found')
                    # if playing_surface is None: exit(0)
                elif key == ord('q'):
                    break

            # Gesture recognition state            
            elif state == 1:
                frame_contour = gesture.detect(transformed, playing_surface)

                # Add dealer and player regions to the displayed surface
                display.regions(frame_contour, playing_surface)
                display.hand_values(frame_contour, playing_surface,
                                    all_cards, state)
                display.bet(frame_contour, playing_surface, all_chips)

                # Show final image with contour
                # cv2.namedWindow("Gesture Recognition", cv2.WINDOW_NORMAL)
                cv2.imshow("Blackjack Tracker", frame_contour)
                # cv2.resizeWindow("Gesture Recognition", 700, 700)
                cv2.moveWindow("Blackjack Tracker", 50, 50)

                key = cv2.waitKey(delay=1)

                if key == ord('t'):
                    # cv2.destroyAllWindows()
                    state = not state
                elif key == ord('c'):
                    playing_surface = surface.get_surface(cap, 10)
                    # print('Recalibration failed. No successful transform found')
                    # if playing_surface is None: exit(0)
                elif key == ord('q'):
                    break

    else:
        print('Initialisation failed. No successful transform found')

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


def imageTest():
    """ Run the blackjack program on test images """

    # Get all the images in the directory
    listing = os.listdir('benchmark_images')

    last_cards = []

    # Loop through the test images
    for files in listing:
        if files.endswith('.png'):

            # Get next image of playing area
            img = cv2.imread(os.path.join(benchmark_img_dir,files))

            # obtain playing surface object
            playing_surface = surface.detect(img)
            transformed = playing_surface.transform
            img_disp = copy.deepcopy(transformed)

            # Get a list of card objects in the image and draw on temp image
            all_cards = cards.detect(transformed, rank_path, last_cards)
            img_disp = cards.display(img_disp, all_cards)

            # Find all of the chips and draw them on the temp image
            all_chips = chips.detect(transformed)
            img_disp = chips.display(img_disp, all_chips)

            # configure images for display and then display them
            cnt_disp = copy.deepcopy(imutils.resize(playing_surface.img_cnt, height=300))

            # Add dealer and player regions to the displayed surface
            #display.regions(img_disp, playing_surface)
            #display.hand_values(img_disp, playing_surface, all_cards)

            while True:
                #cv2.imshow("Playing surface contour", cnt_disp)
                cv2.imshow("Detected Cards and Chips", img_disp)
                key = cv2.waitKey(delay=1)
                if key == ord('q'):
                    cv2.destroyAllWindows()
                    cv2.imwrite(os.path.join(benchmark_res_dir,files),img_disp)
                    break

### Module Test Code ###
if __name__ == "__main__":
    videoTest()
