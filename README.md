# Medicaid_2019_Qual_Measure
Visualization Project on the [2019 Medicaid Quality Measure Dataset](https://data.medicaid.gov/dataset/e36d89c0-f62e-56d5-bc7e-b0adf89262b8).

Please note that the graphs are rendered through nbviewer by clicking on the circle icon located in the upper right corner of the notebook. Or click on [View A](https://nbviewer.jupyter.org/github/corpuzn12/Medicaid_2019_Qual_Measure/blob/fcf0a1a5b052dbdd2b1dba4831adaa51ca725322/2019Medicaid.ipynb) or [View B](https://nbviewer.jupyter.org/github/corpuzn12/Medicaid_2019_Qual_Measure/blob/fcf0a1a5b052dbdd2b1dba4831adaa51ca725322/View%20B.ipynb).

## This visualization project has the following design goals: 
### Overview Across all Measure Types by State (View A)
CMS currently provides simple visualizations that allow users to select a specific state and measure name. However, this approach requires multiple visualizations for a single state and measure, as states typically track several measures within a given domain.
To address this limitation, we propose a more practical visualization that provides a domain-level snapshot of each state. This approach would enable users to quickly identify areas where a state is underperforming or excelling within a specific domain. By focusing on the five primary domains, we reduce the effort required in gathering the relevant insights for a given state. </p> 

**Sample Visual:**
<img src="https://user-images.githubusercontent.com/29220349/131366354-5e957cb5-01fe-4218-8535-f431b9bb1adf.JPG" width="90%"></img> </p> 
Through this view, stakeholders can easily spot the Measures in a given domain where a given state is falling behind. 
 
### Overview Across all States by Measure  Type (View B) 
 </p>
Another valuable visualization would be a comparative snapshot of all states relative to a specific measure type. By arranging states in ascending or descending order based on their rates for a shared measure, users can easily identify top, median, and bottom-performing states.
<img src="https://user-images.githubusercontent.com/29220349/134825488-439ed5fa-b1cb-4211-a211-2d17f262d912.JPG" width="90%"></img>

### Ambiguity with the Dataset </p> 
As illustrated below, some entries have identical information except for the values in 'State Rate' and the corresponding 'Median', 'Top' and 'Bottom Values'. The original dataset lacked dates or other distinguishing features that would indicate the accuracy of one entry over another. Given this ambiguity, we opted to retain the first instance of each unique entry for practical purposes.
<img src="https://user-images.githubusercontent.com/29220349/134824766-d20a9546-c3b4-4d96-bb69-914f7f6fd7c3.JPG" width="90%"></img> </p> 


