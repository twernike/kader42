# CMake generated Testfile for 
# Source directory: /home/thomas/git/kader42/kader42-packages/kader42-core/kcm-kader42-audioguard
# Build directory: /home/thomas/git/kader42/kader42-packages/kader42-core/kcm-kader42-audioguard/build-kcm
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(appstreamtest "/usr/bin/cmake" "-DAPPSTREAMCLI=/usr/bin/appstreamcli" "-DINSTALL_FILES=/home/thomas/git/kader42/kader42-packages/kader42-core/kcm-kader42-audioguard/build-kcm/install_manifest.txt" "-P" "/usr/share/ECM/kde-modules/appstreamtest.cmake")
set_tests_properties(appstreamtest PROPERTIES  _CMAKE_TEST_BUILD_DEPENDS "" _BACKTRACE_TRIPLES "/usr/share/ECM/kde-modules/KDECMakeSettings.cmake;177;add_test;/usr/share/ECM/kde-modules/KDECMakeSettings.cmake;195;appstreamtest;/usr/share/ECM/kde-modules/KDECMakeSettings.cmake;0;;/home/thomas/git/kader42/kader42-packages/kader42-core/kcm-kader42-audioguard/CMakeLists.txt;15;include;/home/thomas/git/kader42/kader42-packages/kader42-core/kcm-kader42-audioguard/CMakeLists.txt;0;")
