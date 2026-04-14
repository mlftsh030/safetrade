# SafeTrade

SafeTrade is a  project exploring how to improve trust and safety in peer-to-peer online marketplace transactions in South Africa, with an initial focus on platforms such as Facebook Marketplace.

The project was initiated from a purchase experience that highlighted a broader issue: informal digital marketplaces often operate without reliable mechanisms for payment security, product assurance, or user accountability. SafeTrade approaches this problem methodically, moving from analysis and validation to system design and eventual implementation.

---

## Overview

SafeTrade is developed as a staged process rather than a single build. The goal is to understand the problem, validate whether it is meaningful and widespread, and design a solution based on evidence.

The project focuses on:
- understanding transaction risks in informal marketplaces
- validating user concerns and behaviours
- testing whether a safer transaction process would be adopted
- designing a system informed by research and data

---

## Problem Context

Peer-to-peer marketplaces allow individuals to transact directly, but they often lack:

- secure payment handling
- structured delivery coordination
- user verification mechanisms
- accountability after transaction failure

This creates exposure to:
- payment fraud
- misrepresented or non-delivered products
- unsafe in-person exchanges
- unresolved disputes

In the South African context, these risks can reduce confidence in online transactions, particularly for higher-value items.

---

## Project Journey

The project is developed across four stages:

Analysis → Design → Implementation → Testing

Each stage builds on the previous one and is supported by documentation.

---

### 1. Analysis

The analysis stage focuses on understanding the problem and validating assumptions before any system is built. This includes defining the nature of transaction risks and their impact on users, identifying the key stakeholders involved in marketplace transactions, outlining the core assumptions such as trust, willingness to pay, and workflow adoption, and examining adoption, operational, and trust-related risks that may affect the solution. It also involves designing a structured market validation approach to test both the problem and the proposed solution using user research and behavioural signals.

#### Validation Prototype

As part of this stage, a lightweight prototype has been developed to collect data directly from users. The purpose of the prototype is to communicate the problem in a simple way and gather feedback on user experiences, concerns, and willingness to adopt a safer transaction process. Data collection is currently ongoing.

The prototype is implemented as a web-based interface using vanilla HTML, CSS, and JavaScript. It presents a structured set of questions and captures user responses, which are stored using a simple backend setup integrated with Google Forms/Sheets.

Live prototype: https://safetradesa.netlify.app/

#### Documentation

All analysis-related work is documented in a single consolidated file:

docs/analysis.md

#### Data Collection

User responses from the validation prototype are captured and stored in a structured format using Google Forms and Google Sheets. This allows responses to be collected in real time and organised for further analysis.

The dataset is continuously updated as new responses are submitted through the prototype.

Data source: [View collected responses](https://docs.google.com/spreadsheets/d/1r6E68lyiUEvV0gx1HkQS1EkL_OjyOrtwcKsYi4jsuqk/edit?usp=sharing)

---

## Repository Structure

```text
safetrade/
├── app/                # frontend prototype
├── docs/               # project documentation
├── research/           # validation and analysis
├── README.md
└── proposal.pdf
```
## Current Status

**Stage:** Analysis and Validation

The project is currently focused on:

- understanding the problem  
- collecting user data  
- testing assumptions through a prototype  

The next stage will depend on the outcome of the validation process.

---

