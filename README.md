## Harrys_Project - ReadMe

### Objective:
**This exercise provides two tables of data and poses the open-ended question of "what insights can you derive from this?"**

### My Steps
**1.** Observe the data in Excel - I noticed a join could be made between the two tables on the key "viewable_product_id"]

**2.** While in Excel, I joined the tables and created several new columns allowing me to ultimately generate a column called "customer_subscription_change_flag".
As the name suggests, this allows me to see which customers modified their subscription of Harry's Razor products. The goal here was to compare customers who did not change their subscription to those who did modify what they received and analyze if subscription modification help customer retention 

**3.** I was then able to export this Excel file to Power BI to generate visuals and capture insights. As I put together my dashboard the story I was trying to tell came to life - and in some cases, sent me back to Excel for further data manipulation. A live link to the Power BI dashboard is available.

**4.** Once I finished visualizing the data, I wanted to complete the same data manipulation steps I had taken in Excel, in Python Pandas. This step eliminates the manual analysis I did in Excel. I did this step at the end because, with this being the first time I had seen or worked with the data, Excel allowed me to explore the data more easily. With the Python code I have written, this data files could be processed hundreds of times each day without issue, ultimately adding automation to the project pipeline. 

## File Glossary
**1. excercise_data.xlsx** - this is the source data provided (note the file has two tabs)

**2. data_excel_export** - this shows the manual Excel analysis I completed including some advanced calculations like nested if statements, index/match statements, and unique/filter statements

**3. data_python_export** - this is the Python file that replaces the steps done in Excel, or in other words is the automated version of my prior manual work

**4. PowerBI_Dashboard_Interactive** This is a text file containing the link to my live, interactive Power BI dashboard

**5. Findings_Jacob_Shughrue.pptx** This is a PowerPoint presentation summarizing my findings

With any questions, don't hesitate to reach out.
