const ruleBuilder = document.getElementById('rule-builder');
const SellConditionContainer = document.getElementById('selling-rules');
const Buy_squareoff_conditionContainer = document.getElementById('buying-sqroff-rules');
const Sell_squareoff_conditionContainer = document.getElementById('selling-sqroff-rules');


function createRuleGroup(json) {
    const groupDiv = document.createElement('div');
    groupDiv.className = 'rule-group';

    const conditionSelect = document.createElement('select');
    conditionSelect.innerHTML = `
        <option value="AND">AND</option>
        <option value="OR">OR</option>
    `;
    conditionSelect.value = json.conditionOperator;
    groupDiv.appendChild(conditionSelect);

    json.conditions.forEach(rule => {
        if (rule.conditions) {
            const subgroup = createRuleGroup(rule);
            groupDiv.appendChild(subgroup);
        } else {
            const ruleDiv = createRule(rule);
            groupDiv.appendChild(ruleDiv);
        }
    });

    const addRuleBtn = document.createElement('button');
    addRuleBtn.innerText = 'Add rule';
    addRuleBtn.onclick = () => {
        const newRule = createRule({ condition: '', Operator: '', Value: '' });
        groupDiv.insertBefore(newRule, addRuleBtn);
    };
    groupDiv.appendChild(addRuleBtn);

    const addGroupBtn = document.createElement('button');
    addGroupBtn.innerText = 'Add group';
    addGroupBtn.onclick = () => {
        const newGroup = createRuleGroup({ conditionOperator: 'AND', conditions: [] });
        groupDiv.insertBefore(newGroup, addRuleBtn);
    };
    groupDiv.appendChild(addGroupBtn);

    return groupDiv;
}

function createRule(rule) {
    const ruleDiv = document.createElement('div');
    ruleDiv.className = 'rule';

    const conditionSelect = document.createElement('select');
    conditionSelect.innerHTML = `
        <option value="RSI">RSI</option>
        <option value="VWAP">VWAP</option>
        <option value="SMA">SMA</option>
        <option value="EMA">EMA</option>
        <option value="Previous Close">Previous Close</option>
        <option value="Current Close">Current Close</option>
        <option value="ADX">ADX</option>
        <option value="TimeBased">TimeBased</option>
    `;
    conditionSelect.value = rule.condition;
    ruleDiv.appendChild(conditionSelect);

    const Operator = document.createElement('select');
    Operator.innerHTML = `
        <option value="<">less</option>
        <option value="=">equal</option>
        <option value=">">greater</option>
        <option value="<=">less than equal</option>
        <option value=">=">greater than equal</option>
    `;
    Operator.value = rule.Operator || '';
    ruleDiv.appendChild(Operator);

    const valueInput = document.createElement('input');
    valueInput.type = 'text';
    valueInput.value = rule.Value || rule.Value1 || rule.Value2 || rule.TimeFrame || '';
    ruleDiv.appendChild(valueInput);

    let valueInput2;
    if (rule.condition === 'CloseComparison') {
        valueInput2 = document.createElement('input');
        valueInput2.type = 'text';
        valueInput2.value = rule.Value2 || '';
        ruleDiv.appendChild(Operator);
        ruleDiv.appendChild(valueInput2);
    }

    if (rule.condition === 'TimeBased') {
        Operator.style.display = 'none';
    }

    conditionSelect.onchange = () => {
        if (conditionSelect.value === 'TimeBased') {
            Operator.style.display = 'none';
            if (valueInput2) {
                valueInput2.remove();
                valueInput2 = null;
            }
        } else if (conditionSelect.value === 'CloseComparison') {
            if (!valueInput2) {
                valueInput2 = document.createElement('input');
                valueInput2.type = 'text';
                valueInput2.value = '';
                ruleDiv.appendChild(valueInput2);
            }
        } else {
            Operator.style.display = 'block';
            if (valueInput2) {
                valueInput2.remove();
                valueInput2 = null;
            }
        }
    };

    const deleteBtn = document.createElement('button');
    deleteBtn.innerText = 'Delete';
    deleteBtn.onclick = () => {
        ruleDiv.remove();
    };
    ruleDiv.appendChild(deleteBtn);

    return ruleDiv;
}


function addRuleGroup() {
    const newGroup = createRuleGroup({ conditionOperator: 'AND', conditions: [] });
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
            const Operator = child.children[1].value;
            const value = child.children[2].value;
            conditions.push({ condition, Operator, Value: value });
        } else if (child.className === 'CloseComparison'){
            const condition = child.children[1].value;
            const Operator = child.children[2].value;
            const value = child.children[3].value;
            conditions.push({ condition, Operator, Value:value });
        }else if (child.className === 'rule-group') {
            conditions.push(parseGroup(child));
        }
    }

    return { conditionOperator, conditions };
}


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
buyingHeader.innerText = 'Buying Conditions';
ruleBuilder.appendChild(buyingHeader);
ruleBuilder.appendChild(createRuleGroup(initialJson.Config.BuyCondition));

const sellingHeader = document.createElement('h3');
sellingHeader.innerText = 'Selling Conditions';
SellConditionContainer.appendChild(sellingHeader);
SellConditionContainer.appendChild(createRuleGroup(initialJson.Config.SellCondition));

const buyingsqroffHeader = document.createElement('h3');
buyingsqroffHeader.innerText = 'Buying Squareoff Conditions';
Buy_squareoff_conditionContainer.appendChild(buyingsqroffHeader);
Buy_squareoff_conditionContainer.appendChild(createRuleGroup(initialJson.Config.Buy_squareoff_condition));

const sellingsqroffHeader = document.createElement('h3');
sellingsqroffHeader.innerText = 'Selling Squareoff Conditions';
Sell_squareoff_conditionContainer.appendChild(sellingsqroffHeader);
Sell_squareoff_conditionContainer.appendChild(createRuleGroup(initialJson.Config.Sell_squareoff_condition));
