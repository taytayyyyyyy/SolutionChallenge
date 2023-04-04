# MediVault - Medical Report Sharing and Analysis Application
MediVault is an android application which can be used by hospitals and patients to securely store, analyze, and share medical reports with ease.

```This repository houses the codebase for the front end of the application Medivault, developed for Google Solution Challenge, 2023. ```

To view the client side code, visit [MediVault - Client Side Code](https://github.com/PriyaDebo/MediVault/)


## General Features:
- Different account for patients and hospitals
- Hospital can add report to patients' account by providing their MediVault Id
- Patients can add report to their own account
- Patients can view the analysis of reports uploaded in their account

## Tech Stack:
- Client Side Code: Flutter
- Server Side Code: Flask
- API: Rest API
- Database: MySQL

## How To Use:
**Step 1:**
>[Install Tesseract-OCR on your machine](https://github.com/tesseract-ocr/tessdoc)
>[Install Tensorflow on your machine](https://www.tensorflow.org/install/pip)


**Step 2:**
>Download or clone this repository by using the link given below.
```
https://github.com/progite/SolutionChallenge.git
```
**Step 3:**
>Go to project root and execute the following command in console to get the required dependencies:
```
pip install -r .\requirements.txt
```
**Step 4:**

```To run the server in terminal, go to the directory where app.py is located and run the following code:```
>flask run --host=0.0.0.0 --debug --no-debugger --no-reload

```Once the server is up and running, you can access the apis and communicate with the server```

**Step 5:**
>The various apis hosted by the server are:
* `http://127.0.0.1:5000/login` - ```to login to the application ```
* `http://127.0.0.1:5000/store-patient-details` - ```to store details of newly registered patient ```
* `http://127.0.0.1:5000/store-hospital-details` - ```to store details of newly registered hospital```
* `http://127.0.0.1:5000/add-report` - ```to upload reports to the account of a registered patient```
* `http://127.0.0.1:5000/read-analysis` - ```to generate analysis of uploaded reports of a patient```

**Step 6:**
>You can see example usage of various apis associated with the project in the file titled 
*MediVault.postman_collection* in root directory

