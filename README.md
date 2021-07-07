# File-Syncronization-SynoCloud-HumHub  
Python based script that syncornize files between SynoCloud and HumHub via their API (FileStation&amp;HumHubApi)  

The purpose of this script is to allow communities to access through HumHub their documents stored in a SynoCloud.  

To inform the English speakers the SIREN (**S**ystème d'**I**dentification du **R**épertoire des **EN**treprises), its purpose is to identify companies, it could be translated as 'Business Directory Identification System'.  

Folder tree of SynoCloud side :  
```
.
└── X/
    ├── Communities/
    │   ├── CommunitiesName1 - Departmentnumber/
    │   │   ├── SIREN.txt
    │   │   └── ...
    │   └── CommunitiesName2 - Departmentnumber/
    │       ├── SIREN.txt
    │       └── ...
    └── ...
  ```

The SIREN.txt file contains the siren of the communities only. I used the siren to be able to sync files in the right folder in HumHub.


Folder tree of HumHub side : 
```
.  
├── CommunitiesName1 [SIREN]/  
│   └── ...  
├── CommunitiesName2 [SIREN]/  
│   └── ...  
└── ...  
```
