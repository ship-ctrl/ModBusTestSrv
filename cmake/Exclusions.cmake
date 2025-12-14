# Function to check if a file should be excluded
function(should_exclude_file FILE_PATH RESULT_VAR)
    get_filename_component(filename_we ${FILE_PATH} NAME_WE)
    get_filename_component(filename ${FILE_PATH} NAME)
    
    # Check against excluded patterns (without extension)
    foreach(pattern ${EXCLUDED_FILES})
        if(filename_we MATCHES "${pattern}")
            set(${RESULT_VAR} TRUE PARENT_SCOPE)
            return()
        endif()
    endforeach()
    
    # Check against full filenames
    foreach(fullname ${EXCLUDED_FULLNAMES})
        if(filename STREQUAL fullname)
            set(${RESULT_VAR} TRUE PARENT_SCOPE)
            return()
        endif()
    endforeach()
    
    set(${RESULT_VAR} FALSE PARENT_SCOPE)
endfunction()