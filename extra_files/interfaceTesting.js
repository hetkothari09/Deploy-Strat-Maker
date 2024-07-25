        function testwindow(){
            const result = {{result | tojson | safe}};
            window.alert(JSON.stringify(result, null, 2));
        };


        const ruleBuilder = document.getElementById('rule-builder');
        const SellConditionContainer = document.getElementById('selling-rules');
        const Buy_squareoff_conditionContainer = document.getElementById('buying-sqroff-rules');
        const Sell_squareoff_conditionContainer = document.getElementById('selling-sqroff-rules');

      function createRuleGroup(json, conditions) {
        const groupDiv = document.createElement('div');
        groupDiv.className = 'rule-group';

        const conditionSelect = document.createElement('select');
        conditionSelect.innerHTML = `
            <option value="AND">AND</option>
            <option value="OR">OR</option>
        `;

        conditionSelect.value = json.conditionOperator || 'AND';
        groupDiv.appendChild(conditionSelect);

        (Array.isArray(json.conditions) ? json.conditions : [json.conditions]).forEach(rule => {
            if (rule.conditions) {
                const subgroup = createRuleGroup(rule, conditions);
                groupDiv.appendChild(subgroup);
            } else if (rule) {
                const ruleDiv = createRule(rule, conditions);
                groupDiv.appendChild(ruleDiv);
            }
        });

        const addRuleBtn = document.createElement('button');
        addRuleBtn.innerText = 'Add rule';
        addRuleBtn.onclick = () => {
            const newRule = createRule({ condition: '', Operator: '', Value: '' }, conditions);
            groupDiv.insertBefore(newRule, addRuleBtn);
        };
        groupDiv.appendChild(addRuleBtn);

        const addGroupBtn = document.createElement('button');
        addGroupBtn.innerText = 'Add group';
        addGroupBtn.onclick = () => {
            const newGroup = createRuleGroup({ conditionOperator: 'AND', conditions: [] }, conditions);
            groupDiv.insertBefore(newGroup, addRuleBtn);
        };
        groupDiv.appendChild(addGroupBtn);

        return groupDiv;
    }

      function createRule(rule, conditions) {
        const ruleDiv = document.createElement('div');
        ruleDiv.className = 'rule';

        const conditionSelect = createSelect(conditions);
        conditionSelect.value = rule.condition || '';
        ruleDiv.appendChild(conditionSelect);

        if (rule.condition === 'CloseComparison') {
            const selectValue1 = createSelect(conditions);
            selectValue1.value = rule.Value1 || '';
            ruleDiv.appendChild(selectValue1);

            const operatorSelect = createSelect(['<', '=', '>', '<=', '>='], true);
            operatorSelect.value = rule.Operator || '';
            ruleDiv.appendChild(operatorSelect);

            const selectValue2 = createSelect(conditions);
            selectValue2.value = rule.Value2 || '';
            ruleDiv.appendChild(selectValue2);
        } else {
            if (rule.SubCondition) {
                const subConditionSelect = createSelect(['K', 'D']);
                subConditionSelect.value = rule.SubCondition || '';
                ruleDiv.appendChild(subConditionSelect);
            }

            const operatorSelect = createSelect(['<', '=', '>', '<=', '>='], true);
            operatorSelect.value = rule.Operator || '';
            ruleDiv.appendChild(operatorSelect);

            if (rule.LongPeriod || rule.ShortPeriod) {
                const longPeriodInput = document.createElement('input');
                longPeriodInput.type = 'text';
                longPeriodInput.placeholder = 'Long Period';
                longPeriodInput.value = rule.LongPeriod || '';
                ruleDiv.appendChild(longPeriodInput);

                const shortPeriodInput = document.createElement('input');
                shortPeriodInput.type = 'text';
                shortPeriodInput.placeholder = 'Short Period';
                shortPeriodInput.value = rule.ShortPeriod || '';
                ruleDiv.appendChild(shortPeriodInput);
            } else {
                let valueInput;
                if (rule.condition === 'TimeBased') {
                    valueInput = document.createElement('input');
                    valueInput.type = 'text';
                    valueInput.value = rule.Value || rule.TimeFrame || '';
                    operatorSelect.style.display = 'none';
                } else if (isNaN(rule.Value)) {
                    valueInput = createSelect(conditions);
                    valueInput.value = rule.Value || '';
                } else {
                    valueInput = document.createElement('input');
                    valueInput.type = 'text';
                    valueInput.value = rule.Value || '';
                }
                ruleDiv.appendChild(valueInput);
            }
        }

        conditionSelect.onchange = () => {
            const newRule = { condition: conditionSelect.value, Operator: '', Value: '' };
            const newRuleDiv = createRule(newRule, conditions);
            ruleDiv.replaceWith(newRuleDiv);
        };

        const deleteBtn = document.createElement('button');
        deleteBtn.innerText = 'Delete';
        deleteBtn.onclick = () => {
            ruleDiv.remove();
        };
        ruleDiv.appendChild(deleteBtn);

        return ruleDiv;
    }

      function createSelect(options, isOperator) {
        const select = document.createElement('select');
        options.forEach(option => {
            const opt = document.createElement('option');
            opt.value = option;
            opt.innerText = isOperator ? convertOperator(option) : option;
            select.appendChild(opt);
        });
        return select;
    }

      function convertOperator(operator) {
        switch (operator) {
            case '<': return 'less';
            case '=': return 'equal';
            case '>': return 'greater';
            case '<=': return 'less than equal';
            case '>=': return 'greater than equal';
            default: return operator;
        }
    }

      function addRuleGroup() {
        const newGroup = createRuleGroup({ conditionOperator: 'AND', conditions: [] }, conditionFields);
        ruleBuilder.appendChild(newGroup);
    }

      function parseGroup(groupDiv) {
        const conditionOperator = groupDiv.querySelector('select').value;
        const conditions = [];
        const children = groupDiv.children;

        for (let i = 1; i < children.length - 2; i++) {
            const child = children[i];
            if (child.className === 'rule') {
                const condition = child.children[0].value;
                const subCondition = child.children[1] && child.children[1].tagName === 'SELECT' ? child.children[1].value : null;
                const Operator = child.children[subCondition ? 2 : 1].value;
                const longPeriod = child.children[subCondition ? 3 : 2] && child.children[subCondition ? 3 : 2].placeholder === 'Long Period' ? child.children[subCondition ? 3 : 2].value : null;
                const shortPeriod = child.children[subCondition ? 4 : 3] && child.children[subCondition ? 4 : 3].placeholder === 'Short Period' ? child.children[subCondition ? 4 : 3].value : null;
                const value = longPeriod === null && shortPeriod === null ? child.children[subCondition ? 3 : 2].value : null;

                const conditionObj = { condition, Operator };
                if (subCondition) conditionObj.SubCondition = subCondition;
                if (longPeriod) conditionObj.LongPeriod = longPeriod;
                if (shortPeriod) conditionObj.ShortPeriod = shortPeriod;
                if (value) conditionObj.Value = value;

                conditions.push(conditionObj);
            } else if (child.className === 'rule-group') {
                conditions.push(parseGroup(child));
            }
        }

        return { conditionOperator, conditions };
    }

      function extractConditions(config) {
        const conditions = new Set();

        const extractFromConditions = (conditionList) => {
            (Array.isArray(conditionList) ? conditionList : [conditionList]).forEach(condition => {
                if (condition.condition) {
                    conditions.add(condition.condition);
                }
                if (condition.conditions) {
                    extractFromConditions(condition.conditions);
                }
                if (condition.Value) {
                    conditions.add(condition.Value);
                }
                if (condition.Value1) {
                    conditions.add(condition.Value1);
                }
                if (condition.Value2) {
                    conditions.add(condition.Value2);
                }
            });
        };

        extractFromConditions(config.BuyCondition?.conditions || config.BuyCondition || []);
        extractFromConditions(config.Buy_squareoff_condition?.conditions || config.Buy_squareoff_condition || []);
        extractFromConditions(config.SellCondition?.conditions || config.SellCondition || []);
        extractFromConditions(config.Sell_squareoff_condition?.conditions || config.Sell_squareoff_condition || []);

        return Array.from(conditions);
    }

      const conditionFields = extractConditions(initialJson.Config);

      function getRules() {
        const buyingRules = parseGroup(ruleBuilder.querySelector('.rule-group'));
        const SellCondition = parseGroup(SellConditionContainer.querySelector('.rule-group'));
        const Buy_squareoff_condition = parseGroup(Buy_squareoff_conditionContainer.querySelector('.rule-group'));
        const Sell_squareoff_condition = parseGroup(Sell_squareoff_conditionContainer.querySelector('.rule-group'));

        const fullJson = {
            BuyCondition: buyingRules.conditions,
            SellCondition: SellCondition.conditions,
            Buy_squareoff_condition: Buy_squareoff_condition.conditions,
            Sell_squareoff_condition: Sell_squareoff_condition.conditions
        };

        window.alert(JSON.stringify(fullJson, null, 2));
    }

      const buyingHeader = document.createElement('h3');
      buyingHeader.innerText = 'Buying Condition';
      ruleBuilder.appendChild(buyingHeader);
      ruleBuilder.appendChild(createRuleGroup(initialJson.Config.BuyCondition?.conditions ? initialJson.Config.BuyCondition : { conditionOperator: 'AND', conditions: [initialJson.Config.BuyCondition] }, conditionFields));

      const sellHeader = document.createElement('h3');
      sellHeader.innerText = 'Selling Condition';
      SellConditionContainer.appendChild(sellHeader);
      SellConditionContainer.appendChild(createRuleGroup(initialJson.Config.SellCondition?.conditions ? initialJson.Config.SellCondition : { conditionOperator: 'AND', conditions: [initialJson.Config.SellCondition] }, conditionFields));

      const Buy_squareoff_conditionHeader = document.createElement('h3');
      Buy_squareoff_conditionHeader.innerText = 'Buying Square Off Condition';
      Buy_squareoff_conditionContainer.appendChild(Buy_squareoff_conditionHeader);
      Buy_squareoff_conditionContainer.appendChild(createRuleGroup(initialJson.Config.Buy_squareoff_condition || { conditionOperator: 'AND', conditions: [] }, conditionFields));

      const Sell_squareoff_conditionHeader = document.createElement('h3');
      Sell_squareoff_conditionHeader.innerText = 'Selling Square Off Condition';
      Sell_squareoff_conditionContainer.appendChild(Sell_squareoff_conditionHeader);
      Sell_squareoff_conditionContainer.appendChild(createRuleGroup(initialJson.Config.Sell_squareoff_condition || { conditionOperator: 'AND', conditions: [] }, conditionFields));
