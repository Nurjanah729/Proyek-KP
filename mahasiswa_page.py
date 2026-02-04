streamlit.errors.StreamlitDuplicateElementKey: This app has encountered an error. The original error message is redacted to prevent data leaks. Full error details have been recorded in the logs (if you're on Streamlit Cloud, click on 'Manage app' in the lower right of your app).

Traceback:
File "/mount/src/proyek-kp/app.py", line 429, in <module>
    main()
    ~~~~^^
File "/mount/src/proyek-kp/app.py", line 424, in main
    admin_dashboard()
    ~~~~~~~~~~~~~~~^^
File "/mount/src/proyek-kp/app.py", line 407, in admin_dashboard
    mahasiswa_page()
    ~~~~~~~~~~~~~~^^
File "/mount/src/proyek-kp/mahasiswa_page.py", line 65, in mahasiswa_page
    st.file_uploader("Upload File", type=["csv"], key="file_import")
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/metrics_util.py", line 531, in wrapped_func
    result = non_optional_func(*args, **kwargs)
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/elements/widgets/file_uploader.py", line 441, in file_uploader
    return self._file_uploader(
           ~~~~~~~~~~~~~~~~~~~^
        label=label,
        ^^^^^^^^^^^^
    ...<10 lines>...
        ctx=ctx,
        ^^^^^^^^
    )
    ^
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/elements/widgets/file_uploader.py", line 483, in _file_uploader
    element_id = compute_and_register_element_id(
        "file_uploader",
    ...<10 lines>...
        width=width,
    )
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/elements/lib/utils.py", line 265, in compute_and_register_element_id
    _register_element_id(ctx, element_type, element_id)
    ~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/elements/lib/utils.py", line 145, in _register_element_id
    raise StreamlitDuplicateElementKey(user_key)
