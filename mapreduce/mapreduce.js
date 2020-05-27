{
  "_id": "_design/designs",
  "_rev": "9-cf1abe1e677aa160ffef732197fb4f82",
  "language": "javascript",
  "views": {
    "agg_by_region": {
      "map": "function (doc) {\n    key = {\n      \"name\": doc.suburb\n    }\n    value = doc.score\n    emit(key, value)\n}",
      "reduce": "function (keys, values, rereduce) {\n  return_value = {\n      \"positive\": 0,\n      \"negative\": 0,\n      \"neutral\": 0,\n      \"total\": 0\n    };\n  if (rereduce) {\n    for (value in values){\n      return_value.positive += values[value].positive\n      return_value.negative += values[value].negative\n      return_value.neutral += values[value].neutral\n      return_value.total += values[value].total\n    }\n    return return_value\n\n  } else {\n    for (value in values){\n      if (values[value].pos>values[value].neg){\n        return_value.positive += 1\n      }\n      else if (values[value].pos<values[value].neg){\n        return_value.negative += 1;\n      }\n      else{\n        return_value.neutral += 1;\n      }\n      return_value.total += 1;\n    }\n    return return_value;\n  }\n}"
    }
  }
}