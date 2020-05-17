# trucrawler
True Crawler 


Definition : 
    
    True Crawler is an automatic tester for apk which crawls through the APK file provided and creates and executes tests in a self-sustainable automated fashion application and provides results. It will scan through the app in an automated way and provide us the statistical and intelligent comparison against previous builds. 

How is it different from other crawlers? :

    Comparison Algo : With block hashing and graph structure for comparison, we accomplish fast and large data comparison
    Crash Reports
    Collection of statistical data for intelligent modification of expected data 
    Performance results
    Configurations for user specific data
    Tree structure for result with snapshot


Results : 

    1. Snapshots for Run : Contains all the snapshot with their IDs
    2. Differences : Contains all the difference in runs
    3. Crash reports : Report logs for crashes
    4. ADB logs : Adb logs for reports
    5. Performance 
    
How to Run? : 

    1. Configure the Config.py as per the requirement and details like device to run and package names.
    2. In config.py enter the input strings you want to enter while crawling 
    3. Now after configuration done , run the below command :
    
        python crawler.py <Crawler duration>
        
        Crawler duration is the duration to run crawler in seconds
        
Results files : 

    REPORT.html contain the report generated.