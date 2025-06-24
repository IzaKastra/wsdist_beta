# wsdist_beta
 
GUI application for simulating damage dealt with various spells and abilities using user-defined gear sets.

You may run the code with as a simple Python file:

    python gui_wsdist.py

or you may simple double-click the gui_wsdist.exe executable. 


The executable was compiled using the following command within the Windows10 powershell:

    pyinstaller --exclude-module gear --exclude-module enemies --clean --onefile .\gui_wsdist.py


If you choose to use the executable version of this application, then I recommend downloading the application from the actions page for this repository (https://github.com/IzaKastra/wsdist_beta/actions), which contains the executable and necessary files for running it in one simple download ("wsdist-full" contains all necessary files; "wsdist-executable-only" contains only the executable). The executable provided on the actions page was created on GitHub servers using the commands found in the "workflow file" and can therefore be verified as "probably safe to run." This is safer than trusting the executable I've uploaded myself.

Note that the application will not notice any changes made to the version .py files (except gear.py) when using the executable version of the code. If you wish to make changes to any other file, then you will need to run the gui_wsdist.py version of the code.


I prefer that all issues are reported as issues on the GitHub page. I rarely check FFXIAH, so I may be delayed when responding to posts there.



GUI preview images:

<img src="https://i.imgur.com/pswkepe.png" alt="Inputs tab preview" width="857" height="454">
<img src="https://i.imgur.com/4mLpiJB.png" alt="Optimize tab preview" width="857" height="454">
<img src="https://i.imgur.com/LTptfE4.png" alt="Player Stats tab preview" width="857" height="454">
<img src="https://i.imgur.com/ZfuJHuA.png" alt="Simulations tab preview" width="857" height="454">
