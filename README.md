## A. Executive Summary

Our analysis of the Open Food Facts snack dataset (High Protein ≥45g/100g, Low Sugar <10g/100g) shows that "Blue Ocean" products are extremely rare overall, and that normalizing each category's Blue Ocean count by its own size — rather than raw counts — reveals **Sweets & Candies** as the true under-served gap, at just 0.09% penetration versus 0.64% for Savory Snacks, the category where this combination is currently most common. This makes Sweets & Candies the clearest opportunity for the new "Healthy Snacking" line, since consumers already buy heavily into this aisle but almost nothing on the shelf combines a meaningful protein claim with a low-sugar profile. Among the handful of products that already succeed in this niche, whey and soy protein each drive protein content in roughly 10% of cases, followed by cheese at ~6%, pointing to a dairy- or soy-protein-based formulation as the most proven path to a high-protein claim. Our recommendation: build a Sweets & Candies product formulated at or above 63g protein and below 1g sugar per 100g — the median profile of the small cluster of products that already occupy this space, a combination almost no current competitor in that category offers.


## B. Project Links
- Link to Notebook: [Notebook Link](https://colab.research.google.com/drive/12ah_dBhWhUTsv2qRKqfnL7gzr2untKPP?usp=sharing)

- Link to Dashboard:

- Link to Presentation:  


## C. Technical Explanation

### Data Cleaning

We worked with a manageable subset of the Open Food Facts CSV rather than the full 3GB+ file. The following cleaning steps were applied before analysis:

- **Missing values:** Rows with null or empty `product_name`, `sugars_100g`, or `proteins_100g` were dropped, since these fields are required for both the categorization logic and the scatter plot — imputing them risked fabricating data points that don't exist in reality.
- **Outliers / biologically impossible values:** Rows where `sugars_100g` or `proteins_100g` fell outside the 0–100g range were removed, along with rows where the two combined exceeded 100g per 100g of product — both are physically impossible for a "per 100g" nutrition figure and stem from data entry errors.
- **Category parsing:** The `categories_tags` column (a comma-separated string of granular tags like `en:chocolate-chip-cookies-with-nuts`) was lowercased, cleaned, and mapped via keyword matching into a `primary_category` column with five high-level buckets: Bakery & Biscuits, Sweets & Candies, Savory Snacks, Dairy Products, and Beverages.
- **Output:** The cleaned result was exported to `cleaned_snacks.csv`, which the Streamlit dashboard (`app.py`) loads directly — keeping the analysis reproducible without relying on local file paths.

### Candidate's Choice Addition

We added a **true Blue Ocean penetration rate by category** metric and chart — the percentage of each category's own products that are already High Protein (≥45g/100g) / Low Sugar (<10g/100g) — instead of relying on raw Blue Ocean product counts.

This mattered in practice, not just in theory: our first pass at this analysis looked at raw counts and Savory Snacks/Bakery & Biscuits data in isolation, which pointed toward the wrong category. Savory Snacks has the most Blue Ocean products in absolute terms (29), which could tempt a team to conclude that category is the opportunity — but Savory Snacks is also where high-protein, low-sugar formulation is *already most common* (0.64% penetration), not where the gap is. Once we normalized every category by its own size, Sweets & Candies stood out as having the lowest true penetration (0.09%) despite having very few Blue Ocean products in absolute terms (5) — because it's also a large category, so that thin slice represents a genuine, largely untapped gap. Normalizing by category size turned this from a counting exercise into a real gap-finding tool, which is the actual point of a Blue Ocean analysis, and it changed our final recommendation.

### Note on Threshold Sensitivity

The High Protein / Low Sugar thresholds (currently 45g / 10g per 100g) were tightened during this project from an earlier working version (15g / 5g). Because Bakery & Biscuits and Sweets & Candies sit very close together in true penetration (0.12% vs. 0.09%) at the current thresholds, the "winning" category is sensitive to where exactly these cutoffs are drawn. We recomputed the recommendation from scratch under the current thresholds rather than carrying over the earlier conclusion, and we'd recommend the same discipline — recompute the full cross-category comparison, don't just re-filter one category — any time the thresholds change again.

# Project Brief: The "Sugar Trap" Market Gap Analysis

**Client:** Helix CPG Partners (Strategic Food & Beverage Consultancy)  
**Deliverable:** Interactive Dashboard, Code Notebook & Insight Presentation

---

## 1. Business Context
**Helix CPG Partners** advises major food manufacturers on new product development. Our newest client, a global snack manufacturer, wants to launch a "Healthy Snacking" line. They believe the market is oversaturated with sugary treats, but they lack the data to prove where the specific gaps are.

They have hired us to answer one question: **"Where is the 'Blue Ocean' in the snack aisle?"**

Specifically, they are looking for product categories that are currently under-served—areas where consumer demand for health (e.g., High Protein, High Fiber) is not being met by current product offerings (which are mostly High Sugar, High Fat).

## 2. The Data
You will use the **Open Food Facts** dataset, a free, open, and massive database of food products from around the world.

* **Source:** [Open Food Facts Data](https://world.openfoodfacts.org/data)
* **Format:** CSV (Comma Separated Values)
* **Warning:** The full dataset is massive (over 3GB). You are **not** expected to process the entire file. You should filter the data early or work with a manageable subset (e.g., the first 500,000 rows or specific categories).

## 3. Tooling Requirements
You have the flexibility to choose your development environment:

* **Option A (Recommended):** Use a cloud-hosted notebook like **Google Colab**, or **Deepnote**, etc.
* **Option B:** Use a local **Jupyter Notebook** or **VS Code**.
    * *Condition:* If you choose this, you must ensure your code is reproducible. Do not reference local file paths (e.g., `C:/Downloads/...`). Assume the dataset is in the same folder as your notebook.
* **Dashboarding:** The final output must be a **publicly accessible link** (e.g., Tableau Public, Google Looker Studio, Streamlit Cloud, or PowerBI Web).

---

## 4. User Stories & Acceptance Criteria

### Story 1: Data Ingestion & "The Clean Up"
**As a** Strategy Director,  
**I want** a clean dataset that removes products with erroneous nutritional information,  
**So that** my analysis is not skewed by bad data entry.

* **Acceptance Criteria:**
    * Handle missing values: Decide what to do with rows that have `null` or empty `sugars_100g`, `proteins_100g`, or `product_name`.
    * Handle outliers: Filter out biologically impossible values.
    * **Deliverable:** A cleaned Pandas DataFrame or SQL table export.

### Story 2: The Category Wrangler
**As a** Product Manager,  
**I want** to group products into readable high-level categories,  
**So that** I don't have to look at 10,000 unique, messy tags like `en:chocolate-chip-cookies-with-nuts`.

* **Acceptance Criteria:**
    * The `categories_tags` column is a comma-separated string (e.g., `en:snacks, en:sweet-snacks, en:biscuits`). You must parse this string.
    * Create a logic to assign a "Primary Category" to each product based on keywords.
    * Create at least 5 distinct high-level buckets.

### Story 3: The "Nutrient Matrix" Visualization
**As a** Marketing Lead,  
**I want** to see a Scatter Plot comparing Sugar (X-axis) vs. Protein (Y-axis) for different categories,  
**So that** I can visually spot where the products are clustered.

* **Acceptance Criteria:**
    * Create a dashboard (PowerBI, Tableau, Streamlit, or Python-based charts) displaying this relationship.
    * Allow the user to filter the chart by the "High Level Categories" you created in Story 2.
    * **Key Visual:** Identify the "Empty Quadrant" (e.g., High Protein + Low Sugar).

### Story 4: The Recommendation
**As a** Client,  
**I want** a clear text recommendation on what product we should build,  
**So that** I can take this to the R&D team.

* **Acceptance Criteria:**
    * On the dashboard, include a "Key Insight" box.
    * Complete this sentence: *"Based on the data, the biggest market opportunity is in [Category Name], specifically targeting products with [X]g of protein and less than [Y]g of sugar."*

---

## 5. Bonus User Story: The "Hidden Gem"
**As a** Health Conscious Consumer,  
**I want** to know which specific ingredients are driving the high protein content in the "good" products,  
**So that** I can replicate this in our new recipe.

* **Acceptance Criteria:**
    * Analyze the `ingredients_text` column for products in your "High Protein" cluster.
    * Extract and list the Top 3 most common protein sources (e.g., "Whey", "Peanuts", "Soy").

---

## 6. The "Candidate's Choice" Challenge
**As a** Creative Analyst,  
**I want** to add one additional feature or analysis to this project that I believe provides massive value,  
**So that** I can show off my business acumen.

* **Instructions:**
    * Add one more chart, filter, or metric that wasn't asked for.
    * Explain **why** you added it.
    * **There is no wrong answer, but you must justify your choice.**

---

## 7. Submission Guidelines
Please edit this `README.md` file in your forked repository to include the following three sections at the top:

### A. The Executive Summary
* A 3-5 sentence summary of your findings.

### B. Project Links
* **Link to Notebook:** (e.g., Google Colab, etc.). *Ensure sharing permissions are set to "Anyone with the link can view".*
* **Link to Dashboard:** (e.g., Tableau Public / Power BI Web, etc.).
* **Link to Presentation:** A link to a short slide deck (PDF, PPT) AND (Optional) a 2-minute video walkthrough (YouTube) explaining your results.

### C. Technical Explanation
* Briefly explain how you handled the "Data Cleaning".
* Explain your "Candidate's Choice" addition.

**Important Note on Code Submission:**
* Upload your `.ipynb` notebook file to the repo.
* **Crucial:** Also upload an **HTML or PDF export** of your notebook so we can see your charts even if GitHub fails to render the notebook code.
* Once you are ready, please fill out the [Official Submission Form Here](https://forms.office.com/e/heitZ9PP7y) with your links

---

## 🛑 CRITICAL: Pre-Submission Checklist

**Before you submit your form, you MUST complete this checklist.**

> ⚠️ **WARNING:** If you miss any of these items, your submission will be flagged as "Incomplete" and you will **NOT** be invited to an interview. 
>
> **We do not accept "permission error" excuses. Test your links in Incognito Mode.**

### 1. Repository & Code Checks
- [ ] **My GitHub Repo is Public.** (Open the link in a Private/Incognito window to verify).
- [ ] **I have uploaded the `.ipynb` notebook file.**
- [ ] **I have ALSO uploaded an HTML or PDF export** of the notebook.
- [ ] **I have NOT uploaded the massive raw dataset.** (Use `.gitignore` or just don't commit the CSV).
- [ ] **My code uses Relative Paths.** 

### 2. Deliverable Checks
- [ ] **My Dashboard link is publicly accessible.** (No login required).
- [ ] **My Presentation link is publicly accessible.** (Permissions set to "Anyone with the link can view").
- [ ] **I have updated this `README.md` file** with my Executive Summary and technical notes.

### 3. Completeness
- [ ] I have completed **User Stories 1-4**.
- [ ] I have completed the **"Candidate's Choice"** challenge and explained it in the README.

**✅ Only when you have checked every box above, proceed to the submission form.**

---
