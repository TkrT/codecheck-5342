"use strict";

const assert = require("chai").assert;
const codecheck = require("codecheck");

describe("jsontest", () => {
  const app = codecheck.consoleApp(process.env.APP_COMMAND);
  const cases = require('./cases.json');

  cases.forEach((c) => {
    let description = c.it || `${c.input} -> ${JSON.stringify(c.output)}`;
    it(description, () => {
      console.log(c.input)
      return app.codecheck(c.input)
        .then(result => {
          assert.equal(result.code, 0);
          assert.equal(result.stdout[0], JSON.stringify(c.output));
        });
    });
  });
});
