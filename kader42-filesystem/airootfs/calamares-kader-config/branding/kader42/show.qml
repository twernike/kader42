/* === This file is part of Calamares - <https://calamares.io> ===
 *
 * SPDX-FileCopyrightText: 2015 Teo Mrnjavac <teo@kde.org>
 * SPDX-FileCopyrightText: 2018 Adriaan de Groot <groot@kde.org>
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 * Calamares is Free Software: see the License-Identifier above.
 *
 */

import QtQuick 2.0;
import calamares.slideshow 1.0;

Presentation
{
    id: presentation

    function nextSlide() {
        //console.log("QML Component (default slideshow) Next slide");
        presentation.goToNextSlide();
    }

    Timer {
        id: advanceTimer
        interval: 10000
        running: presentation.activatedInCalamares
        repeat: true
        onTriggered: nextSlide()
    }

    Slide {

        Image {
            id: promo1
            source: "/usr/share/calamares/branding/kader42/images/wallpaper-01.jpg"
            fillMode: Image.PreserveAspectFit
            anchors.centerIn: parent
        }
    }


    Slide {

        Image {
            id: promo2
            source: "/usr/share/calamares/branding/kader42/images/wallpaper-02.jpg"
            fillMode: Image.PreserveAspectFit
            anchors.centerIn: parent
        }
    }

    Slide {

        Image {
            id: promo3
            source: "/usr/share/calamares/branding/kader42/images/wallpaper-03.jpg"
            fillMode: Image.PreserveAspectFit
            anchors.centerIn: parent
        }
    }

    Slide {

        Image {
            id: promo4
            source: "/usr/share/calamares/branding/kader42/images/wallpaper-04.jpg"
            fillMode: Image.PreserveAspectFit
            anchors.centerIn: parent
        }
    }

    Slide {

        Image {
            id: promo5
            source: "/usr/share/calamares/branding/kader42/images/wallpaper-05.jpg"
            fillMode: Image.PreserveAspectFit
            anchors.centerIn: parent
        }
    }

    Slide {

        Image {
            id: promo6
            source: "/usr/share/calamares/branding/kader42/images/wallpaper-06.jpg"
            fillMode: Image.PreserveAspectFit
            anchors.centerIn: parent
        }
    }

    Slide {

        Image {
            id: promo7
            source: "/usr/share/calamares/branding/kader42/images/wallpaper-07.jpg"
            fillMode: Image.PreserveAspectFit
            anchors.centerIn: parent
        }
    }

    Slide {

        Image {
            id: promo8
            source: "/usr/share/calamares/branding/kader42/images/wallpaper-08.jpg"
            fillMode: Image.PreserveAspectFit
            anchors.centerIn: parent
        }
    }

    Slide {

        Image {
            id: promo9
            source: "/usr/share/calamares/branding/kader42/images/wallpaper-09.jpg"
            fillMode: Image.PreserveAspectFit
            anchors.centerIn: parent
        }
    }

    Slide {

        Image {
            id: promo10
            source: "/usr/share/calamares/branding/kader42/images/wallpaper-10.jpg"
            fillMode: Image.PreserveAspectFit
            anchors.centerIn: parent
        }
    }
    
    Slide {

        Image {
            id: promo11
            source: "/usr/share/calamares/branding/kader42/images/wallpaper-11.jpg"
            fillMode: Image.PreserveAspectFit
            anchors.centerIn: parent
        }
    }

    Slide {

        Image {
            id: promo12
            source: "/usr/share/calamares/branding/kader42/images/wallpaper-12.jpg"
            fillMode: Image.PreserveAspectFit
            anchors.centerIn: parent
        }
    }

    // When this slideshow is loaded as a V1 slideshow, only
    // activatedInCalamares is set, which starts the timer (see above).
    //
    // In V2, also the onActivate() and onLeave() methods are called.
    // These example functions log a message (and re-start the slides
    // from the first).
    function onActivate() {
        console.log("QML Component (default slideshow) activated");
        presentation.currentSlide = 0;
    }

    function onLeave() {
        console.log("QML Component (default slideshow) deactivated");
    }

}