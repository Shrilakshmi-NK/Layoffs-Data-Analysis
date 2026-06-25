-- 1. Remove Duplicates
-- 2. Standardize the Data
-- 3. Null Values or blank values
-- 4. Remove Any Columns

select * from layoffs;

create table layoffs_staging like layoffs;
insert layoffs_staging select * from layoffs;
select * from layoffs_staging;

-- 1. REMOVING DUPLICATES
select *, row_number() over(partition by company, industry, total_laid_off, percentage_laid_off, `date`) as row_num
from layoffs_staging;

with duplicate_cte as(
select *, row_number() over(partition by company, location, industry, total_laid_off, percentage_laid_off, `date`, stage, country, funds_raised_millions) as row_num
from layoffs_staging
)
select * from duplicate_cte where row_num>1;

SELECT *
FROM layoffs_staging
WHERE company = 'Casper';

CREATE TABLE `layoffs_staging2` (
  `company` text,
  `location` text,
  `industry` text,
  `total_laid_off` int DEFAULT NULL,
  `percentage_laid_off` text,
  `date` text,
  `stage` text,
  `country` text,
  `funds_raised_millions` int DEFAULT NULL,
  `row_num` int
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


SELECT *
FROM layoffs_staging2;

insert into layoffs_staging2
select *, row_number() over(partition by company, industry, total_laid_off, percentage_laid_off, `date`) as row_num
from layoffs_staging;


SELECT *
FROM layoffs_staging2 where row_num>1;

delete
FROM layoffs_staging2 where row_num>1;

-- 2. STANDARDIZE THE DATA

-- Trimming withspaces at the beginning of the company name
select  distinct(trim(company)) from layoffs_staging2;
select company, trim(company) from layoffs_staging2;

update layoffs_staging2 set company = trim(company);


SELECT distinct industry
FROM layoffs_staging2 order by 1;

-- Standerdizing all Cypto labels 
SELECT * from layoffs_staging2 where industry like 'Crypto%';
update layoffs_staging2 set industry = 'Crypto' where industry like 'Crypto%';
SELECT distinct industry FROM layoffs_staging2;

SELECT distinct location FROM layoffs_staging2 order by 1;
SELECT distinct country FROM layoffs_staging2 order by 1;

-- Removing '.' at the end of a country
SELECT * FROM layoffs_staging2 where country like 'United States%' order by 1;
SELECT distinct country, trim(trailing '.' from country) FROM layoffs_staging2 order by 1;

update layoffs_staging2 set country = trim(trailing '.' from country)
where country like 'United States%';

select `date` from layoffs_staging2;
-- changing date format to m/d/y
select `date`,str_to_date(`date`, '%m/%d/%Y') from layoffs_staging2;
update layoffs_staging2 set `date`=str_to_date(`date`, '%m/%d/%Y');

-- changing date column data type to date
alter table layoffs_staging2
modify column `date` DATE;

-- 3. NULL VALUES OR BLANK VALUES

select * from layoffs_staging2 where total_laid_off is NULL and percentage_laid_off is null;


SELECT *
FROM layoffs_staging2
WHERE industry IS NULL
OR industry = '';

SELECT *
FROM layoffs_staging2
WHERE company = 'Airbnb';

UPDATE layoffs_staging2
SET industry = NULL
WHERE industry ='';

SELECT *
FROM layoffs_staging2 t1
JOIN layoffs_staging2 t2
ON t1.company = t2.company
WHERE (t1. industry IS NULL OR t1.industry = '')
AND t2. industry IS NOT NULL;

UPDATE layoffs_staging2 t1
JOIN layoffs_staging2 t2
ON t1.company = t2.company
SET t1.industry = t2.industry
WHERE t1.industry IS NULL
AND t2.industry IS NOT NULL;

SELECT *
FROM layoffs_staging2
WHERE company LIKE 'Bally%';

DELETE
FROM layoffs_staging2
WHERE total_laid_off IS NULL
AND percentage_laid_off IS NULL;

ALTER TABLE layoffs_staging2
DROP COLUMN row_num;
