#----------------------------------------------------------------
# Generated CMake target import file for configuration "RelWithDebInfo".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "test_embed_lib" for configuration "RelWithDebInfo"
set_property(TARGET test_embed_lib APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(test_embed_lib PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELWITHDEBINFO "CXX"
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/bin/test_embed_lib.lib"
  )

list(APPEND _cmake_import_check_targets test_embed_lib )
list(APPEND _cmake_import_check_files_for_test_embed_lib "${_IMPORT_PREFIX}/bin/test_embed_lib.lib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
