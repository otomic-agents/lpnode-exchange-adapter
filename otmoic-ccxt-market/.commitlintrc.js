/*
 * 
 */
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [2, 'always', ['init', 'feat', 'fix', 'docs', 'style', 'refactor', 'perf', 'test', 'chore', 'build', 'ci', 'revert']],
    'type-empty': [2, 'never'],
    'scope-enum': [0], 
    'scope-empty': [0], 
    'subject-case': [0], 
    'subject-min-length': [2, 'always', 2],
  },
};
