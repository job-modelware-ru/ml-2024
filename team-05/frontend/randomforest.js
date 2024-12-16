//одно дерево решений
let decision_tree = function (root) {
  let predictOne = function (x) {
    let node = root;
    while (node["type"] == "split") {
      let threshold = node["threshold"].split(" <= ");
      if (x[threshold[0]] <= threshold[1]) {
        //выбираем левое
        node = node["left"];
      } else {
        //выбираем правое
        node = node["right"];
      }
    }
    return node["value"][0];
  };

  let predict = function (X) {
    let pred = [];
    for (let x in X) {
      pred.push(this.predictOne(X[x]));
    }
    return pred;
  };

  return {
    predict: predict,
    predictOne: predictOne,
  };
};

//случайный лес
let random_forest = function (clf) {
  let predict = function (X) {
    let pred = [];
    for (let e in clf["estimators"]) {
      let tree = decision_tree(clf["estimators"][e]);
      pred.push(tree.predict(X));
    }
    pred = pred[0].map((col, i) => pred.map((row) => row[i]));
    let results = [];
    for (let p in pred) {
      let positive = 0,
        negative = 0;
      for (let i in pred[p]) {
        positive += pred[p][i][1];
        negative += pred[p][i][0];
      }
      results.push([positive >= negative, Math.max(positive, negative)]);
    }
    return results;
  };

  return {
    predict: predict,
  };
};
