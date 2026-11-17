cat << 'EOF' > CMakeLists.txt
cmake_minimum_required(VERSION 3.16)
project(kcm_kader42_audioguard)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(ECM REQUIRED NO_MODULE)
set(CMAKE_MODULE_PATH ${ECM_MODULE_PATH})

set(QT_MAJOR_VERSION 6)
find_package(Qt6 REQUIRED COMPONENTS Core Quick)
find_package(KF6 REQUIRED COMPONENTS CoreAddons KCMUtils)

include(KDEInstallDirs)
include(KDECMakeSettings)
include(KDECompilerSettings NO_POLICY_SCOPE)

set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

kcmutils_add_qml_kcm(kcm_kader42_audioguard SOURCES kcm_kader42_audioguard.cpp)
target_link_libraries(kcm_kader42_audioguard PRIVATE
    Qt6::Core
    Qt6::Quick
    KF6::CoreAddons
    KF6::KCMUtils
)
EOF

rm -rf build-kcm
cmake -B build-kcm -S . -DCMAKE_INSTALL_PREFIX=/usr
cmake --build build-kcm
cp build-kcm/bin/plasma/kcms/systemsettings/kcm_kader42_audioguard.so ../usr/lib/qt6/plugins/plasma/kcms/systemsettings/
