# Copyright 2022 Mathworks, Inc.

class _MatlabFinder(build_py):
    """
    Private class that finds MATLAB on user's computer prior to package installation.
    """
    
    def run(self):
        """
        Logic that runs prior to installation.
        """
        print('This branch and its contents are placeholders. See other branches.')

if __name__ == '__main__':

    setup(
        name="matlabengine",
        # MUST_BE_UPDATED_EACH_RELEASE (Search repo for this string)
        version="[version -- see individual repository branches]",
        description='stub -- see individual repository branches',
        author='MathWorks',
        license="stub -- see individual repository branches",
        url='https://github.com/mathworks/matlab-engine-for-python/',
        long_description='stub',
        long_description_content_type="text/markdown",
        package_dir={'': 'src'},
        packages=find_packages(where="src"),
        cmdclass={'build_py': _MatlabFinder},
        package_data={'': ['_arch.txt']},
        zip_safe=False,
        project_urls={
            'Documentation': 'https://www.mathworks.com/help/matlab/matlab-engine-for-python.html',
            'Source': 'https://github.com/mathworks/matlab-engine-for-python',
            'Tracker': 'https://github.com/mathworks/matlab-engine-for-python/issues'
        },
        keywords=[
            "MATLAB",
            "MATLAB Engine for Python"
        ],
        classifiers=[
            "Natural Language :: English",
            "Intended Audience :: Developers",
            # MUST_BE_UPDATED_EACH_RELEASE (Search repo for this string)
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9"
        ],
        # MUST_BE_UPDATED_EACH_RELEASE (Search repo for this string)
        python_requires="[version -- see individual repository branches]"
    )
