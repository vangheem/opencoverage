import Layout from '../../../components/layout'
import { useState } from 'react'
import Highlight from 'react-highlight'

function InstallOpenCoverage ({ params }) {
  return (
    <>
      <h2 className='title'>Install Open Coverage GitHub Application</h2>
      <div className='message is-dark'>
        <div className='message-body'>
          Before you can submit your coverage to the public Open Coverage
          service, you need install the application for your organization.
        </div>
      </div>
      <p>
        Visit the{' '}
        <a href='https://github.com/apps/open-coverage' target='_blank'>
          GitHub App
        </a>{' '}
        and install it for your organization.
      </p>
      <div className='section'>
        <p className='buttons'>
          <a
            target='_blank'
            className='button is-link is-large'
            href='https://github.com/apps/open-coverage'
          >
            <span className='icon is-medium'>
              <i className='fab fa-github'></i>
            </span>
            <span>Install open coverage</span>
          </a>
        </p>
      </div>
      <p>
        After you install the application to your organization, pay attention to
        the installation ID for your organization. You will be using this as a
        token when you upload your coverage report.
      </p>
      <p>
        <img src='/docs/install-id.png' />
      </p>
      <p>
        In this example, the install ID is <span className='tag'>14396163</span>
        .
      </p>
    </>
  )
}

function GenerateCoverage ({ params }) {
  var [lang, setTab] = useState(0)
  if (!lang) {
    lang = 'python'
  }

  return (
    <>
      <div className='tabs'>
        <ul>
          <li className={lang == 'python' ? 'is-active' : ''}>
            <a onClick={() => setTab('python')}>Python/XML Coverage</a>
          </li>
          <li className={lang == 'js' ? 'is-active' : ''}>
            <a onClick={() => setTab('js')}>JavaScript/lcov</a>
          </li>
        </ul>
      </div>
      <div className={lang == 'python' ? '' : 'is-hidden'}>
        Use the Python <a href='https://coverage.readthedocs.io/'>Coverage</a>{' '}
        coverage package to generate an XML coverage report.
        <br />
        Once <span className='tag'>coverage</span> is installed, you just need to produce the XML report.<br />
        <br />
        <Highlight className='sh'>coverage xml</Highlight>
        <br />
        If you're using <a href='https://docs.pytest.org/en/stable/'>pytest</a>, you can also integrate with <span className='tag'>pytest-cov</span> to
        generate it all with once command.<br />
        <br />
        <Highlight className='sh'>
          pytest tests --cov=[mypackage] --cov-report xml
        </Highlight>
      </div>
      <div className={lang == 'js' ? '' : 'is-hidden'}>
        There are multiple options for producing lcov coverage reports.
        <br />
        For example, with `jest`, you will need to configure it with{' '}
        <span className='tag'>jest.config.js</span>:
        <Highlight className='json'>
          {`
module.exports = {
  testPathIgnorePatterns: ['<rootDir>/.next/', '<rootDir>/node_modules/'],
  setupFilesAfterEnv: ['<rootDir>/setupTests.js'],
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': '<rootDir>/node_modules/babel-jest',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy'
  },
  collectCoverageFrom: [
    '**/*.{js,jsx}',
    '!**/node_modules/**',
    '!**/vendor/**',
    '!**/.next/**'
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['text-lcov']
}

`}
        </Highlight>
        This configures jest to produce lcov reports.
        <br />
        Then, create lcov:
        <Highlight className='sh'>{`jest --coverage > coverage.lcov`}</Highlight>
      </div>
    </>
  )
}

function Docs ({ params }) {
  const [tab, setCount] = useState(0)

  return (
    <Layout title='Integration Documentation: Open Coverage'>
      <div className='container'>
        <br />
        <h1 className='title'>Open Coverage Documentation: Integration</h1>
        <p className='subtitle'>Using the public Open Coverage service</p>

        <div className='notification is-danger'>
          Do not integrate with private repositories. Use the self-hosted option
          for private repositories.
        </div>

        <div className='section'>
          <InstallOpenCoverage />
        </div>

        <div className='section'>
          <h2 className='title'>Generate coverage data</h2>
          <div className='message is-dark'>
            <div className='message-body'>
              Next, you'll need to generate coverage data for your test runs.
              This will look different depending on the language you're
              developing with.
            </div>
          </div>
          <GenerateCoverage />
        </div>
        <div className='section'>
          <h2 className='title'>Submit coverage</h2>
          <div className='message is-dark'>
            <div className='message-body'>
              Finally, you need to submit your coverage data to Open Coverage
            </div>
          </div>
          <p>
            The tested method for submitting coverage data is through the Python
            codecov module.
          </p>
          <Highlight className='sh'>pip install codecov</Highlight>
          Then, submit with custom URL:
          <Highlight className='sh'>
            codecov --url="https://open-coverage.org/api" --token=[github
            installation id] --slug=[org]/[repo]
          </Highlight>
          You can also use the <a href='https://www.npmjs.com/package/codecov'>codecov NPM package</a> for Node.js projects:
          <Highlight className='sh'>yarn add codecov</Highlight>
          Submit to open coverage is the same syntax:
          <Highlight className='sh'>{`
codecov --url='https://open-coverage.org/api' --token=14396163 --slug=[org]/[repo] -f coverage.lcov
`}</Highlight>
          There is a suite of client libraries for codecov that should be
          compatible with Open Coverage.
          <div className='section'>
            <p className='subtitle'>Configuration</p>
            <table className='table'>
              <thead>
                <tr>
                  <th>Option</th>
                  <th>Value</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>
                    <b>--token</b>
                  </td>
                  <td>Open Coverage installation ID for your organization</td>
                </tr>
                <tr>
                  <td>
                    <b>--slug</b>
                  </td>
                  <td>
                    Should be <span className='tag'>[org]/[repo]</span>{' '}
                    combination for your repository. For example,{' '}
                    <span className='tag'>vercel/next.js</span>
                  </td>
                </tr>
                <tr>
                  <td>
                    <b>-F</b>
                  </td>
                  <td>
                    Flags allow you to pass information about the coverage
                    report.<br></br> For example, to specify that the report is for a
                    specific project in the repo, use <span className='tag'>-F project:foobar</span>
                    and the report will be categorized separately from others.<br />
                    This is how you can manage mono-repositories and one commit
                    spanning multiple projects.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div className='section'>
          <h2 className='title'>cov.yaml: Configuration</h2>
          <div className='message is-dark'>
            <div className='message-body'>
              To configure projects in your repo, you must have a{' '}
              <span className='tag'>cov.yaml</span>
              file in the root of your repository.
            </div>
          </div>
          <Highlight className='sh'>
            {`
target: 99%
projects:
  frontend:
    base_path: app
  api:
    target: 100%
`}
          </Highlight>
          <div className='section'>
            <table className='table'>
              <thead>
                <tr>
                  <th>Option</th>
                  <th>Value</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>
                    <b>target</b>
                  </td>
                  <td>Global target coverage</td>
                </tr>
                <tr>
                  <td>
                    <b>diff_target</b>
                  </td>
                  <td>Global target coverage on changed code</td>
                </tr>
                <tr>
                  <td>
                    <b>projects</b>
                  </td>
                  <td>Container for project specific settings</td>
                </tr>
                <tr>
                  <td>
                    <b>projects.[name].target</b>
                  </td>
                  <td>Customized target specifically for a project</td>
                </tr>
                <tr>
                  <td>
                    <b>projects.[name].diff_target</b>
                  </td>
                  <td>
                    Customized target coverage on changed code for a project
                  </td>
                </tr>
                <tr>
                  <td>
                    <b>projects.[name].base_path</b>
                  </td>
                  <td>
                    Base path of where coverage report was generated from. This
                    is useful for mono-repos
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </Layout>
  )
}

export default Docs
