Feature: Product Tracking and Scheduling
  As a user
  I want to track product prices, schedule checks, and receive notifications
  So that I never miss a deal

  Scenario: User tracks a Myntra product and receives a notification
    Given the Product Cost Tracker app is running
    When I open the Hunt form
    And I enter a Myntra product URL and a target price below the current price
    And I select the recipient alias "kalyan"
    And I click Track Product
    Then I should see a message that the product is being tracked

  Scenario: User schedules a product for automatic checks
    Given the Product Cost Tracker app is running
    When I open the Hunt form
    And I enter a Myntra product URL and a target price
    And I select the recipient alias "kalyan"
    And I enable scheduling for every 4 hours
    And I click Track Product
    Then the product should appear in the Being Hunted table

  Scenario: User edits a scheduled product using alias
    Given the Product Cost Tracker app is running
    And a product is scheduled
    When I go to the Being Hunted table
    And I click Edit on the product
    And I change the recipient alias to "uma"
    And I save the changes
    Then the product should show "uma" as the recipient

  Scenario: User deletes a scheduled product
    Given the Product Cost Tracker app is running
    And a product is scheduled
    When I go to the Being Hunted table
    And I click Delete on the product
    Then the product should no longer appear in the table
