<div id="top"></div>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
<!-- [![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url] -->



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/othneildrew/Best-README-Template">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">RulesEngineTests</h3>

  <p align="center">
    README for the RulesEngineTestSystems!
    <br />
    <a href="https://team.tecexlabs.dev/tecex-rules-system/docs/"><strong>Explore the RulesEngine docs »</strong></a>
    <br />
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

The TecEx RulesEngine aims to increase the speed of the current website by creating a new backend mimiced from its Salesforce one. This project will test the new RulesEng backend using test cases defined in excel spreadsheets. These are converted to json collections which are passed to Postman using Newman. Results from these tests are stored in a created "temp/diagnostics" folder. Coverage reports can also be created.  

<p align="right">(<a href="#top">back to top</a>)</p>



### Built With

* [![Python][python-coverage.py]][coverage.py-url]

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

This Test system can run in two ways. If you do not need the coverage report for the RulesEng, download the repo and follow the instructions. If you do need the coverage report, the RulesEng should be a package within this project's directory.

The results are stored in the */temp/diagnostics folder.


### Prerequisites

Running the tests requires Newman. 
* npm
  ```sh
  npm install -g newman
  ```

### Installation

_An example on how to setup and install this app._

1. Create a token for the API to update the excels at [https://example.com](https://example.com)
2. Clone the repo
   ```sh
   git clone https://github.com/Nirav-TecEX/RulesEngineTests.git
   ```
3. Install Newman. Visit [https://blog.postman.com/installing-newman-on-windows/](https://blog.postman.com/installing-newman-on-windows/) for a full guide.
   ```sh
   npm install
   ```
4. Install the required libraries using
   ```sh
   pip install -r requirements.txt
   ```
5. Run the code using
   ```sh
   python run_tests.py args
   ```
   or by using the batch file (uses the default json)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

To use this repo, run the "run_tests.py" file from your directory either by using the commandline or by double clicking the batch file. If you run it from the commandline, you can give an argument with the json to use (saved in the root directory). Otherwise, alter the "JsonCommands.json" file in the root directory.

### Run Excel TestSheet Tests 
* Test command
  ```sh
  python run_tests.py <JsonCommands.json>
  ```

The commands in the json should be comma seperated. An example follows.
```json
{
  "test name 1": "-r, temp\\excel_files\\SO_Travel_Notifications.xlsx, -u, <RulesEng endpoint>",
  "test name 2": "-r, temp\\excel_files\\SO_Travel_Notifications1.xlsx", 
  "test name 3": "-g, temp\\excel_files\\SO_Travel_Notifications2.xlsx", 
}
```

*All of the excel files must be in the temp/excel_files folder.*

There are three flags, namely:
* If set, will generate the jsons from the excels and then run the newman collection
  ```sh 
  -r [arg]
  ``` 
* If set, will generate the jsons from the excels
  ```sh 
  -g [arg]
  ```
* If set, specifies which endpoint to use for the REng
  ```sh 
  -u [arg]
  ```

<p align="right">(<a href="#top">back to top</a>)</p>

### Run Code Coverage Audit
* Code Coverage (Parallel) Run command
  ```sh
  coverage run --concurrency=multiprocessing --parallel-mode run run_tests.py <JsonCommands.json>
  ```
* Code Coverage command to combine the output files from each process.
  ```sh
  coverage combine
  ```
* Code Coverage build html command
  ```sh
  coverage html
  ```
* View the html output in your browser of choice by double-clicking on ...\RulesEngineTests\htmlcov\index.html file.  

<!-- ROADMAP -->
## Roadmap

- [x] Run Newman Tests Locally
- [x] Hit the RulesEng at an endpoint with the Requests
- [x] Create a process for the tests
- [x] Process results
    - [x] Filter output and remove unnecessary information
    - [x] Store output
    - [ ] Relay information to testuser
- [ ] Add code coverage
- [ ] Integrate with local RulesEngine
- [ ] Integrate with any locally run RulesEngine
- [ ] Add scheduler to update the local excel files

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Nirav Surajlal - niravs@tecex.com

Project Link: [https://github.com/Nirav-TecEX/RulesEngineTests.git](https://github.com/Nirav-TecEX/RulesEngineTests.git)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [Img Shields](https://shields.io)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[coverage.py-url]: https://pypi.org/project/coverage/
[python-coverage.py]: https://img.shields.io/badge/python-coverage.py-blue
