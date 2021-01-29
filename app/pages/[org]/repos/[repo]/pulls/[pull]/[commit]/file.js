import useSWR from 'swr'
import Layout from '../../../../../../../components/layout'
import ReportLink from '../../../../../../../components/reportlink'
import {
  fetcher,
  apiUrl,
  calcTagClassName,
  rawFetcher,
  fmtNumber
} from '../../../../../../../utils'
import { useRouter } from 'next/router'

function FileLine ({ line, lineno, report, fileCoverage, fileDiff }) {
  lineno = lineno + 1
  var className = 'line'

  if (line) {
    if (fileCoverage.lines[lineno] !== undefined) {
      if (fileCoverage.lines[lineno] == 1) {
        // covered
        className += ' covered'
        if (fileDiff !== null && fileDiff.lines.indexOf(lineno) !== -1) {
          className += ' diff-covered'
        }
      } else {
        className += ' not-covered'
        if (fileDiff !== null && fileDiff.lines.indexOf(lineno) !== -1) {
          className += ' not-diff-covered'
        }
      }
    }
  }
  return (
    <div className={className}>
      <div className='line-number'>{lineno}</div>
      <div className='line-source'>{line.split(' ').join('\u00a0')}</div>
    </div>
  )
}

function File ({ report, filename, fileCoverage, fileDiff }) {
  const resp = useSWR(
    `${apiUrl}/${report.organization}/repos/${report.repo}/commits/${report.commit_hash}/download?filename=${filename}`,
    rawFetcher
  )
  if (!resp.data) {
    return <p>Could not find file</p>
  }
  const lines = resp.data.split(/\r?\n/)
  return (
    <section className='source'>
      {lines.map((line, lineno) => {
        return (
          <FileLine
            key={lineno}
            line={line}
            lineno={lineno}
            report={report}
            fileCoverage={fileCoverage}
            fileDiff={fileDiff}
          />
        )
      })}
    </section>
  )
}

function FileCoverage ({ report, filename }) {
  const { data } = useSWR(
    `${apiUrl}/${report.organization}/repos/${report.repo}/commits/${report.commit_hash}/file?filename=${filename}`,
    fetcher
  )
  if (data && data.reason && data.reason == 'fileNotFound') {
    return <p>Not found</p>
  }
  if (!data) {
    return <div />
  }

  var diff_file_coverage = '-',
    diff_covered_lines = '-',
    diff_missed_lines = '-'
  const fileDiffs = report.pull_diff.filter(diff => diff.filename == filename)
  var fileDiff = null
  if (fileDiffs.length > 0) {
    fileDiff = fileDiffs[0]
    diff_file_coverage = (fileDiff.line_rate * 100).toFixed(1) + '%'
    diff_covered_lines = fmtNumber(fileDiff.hits)
    diff_missed_lines = fmtNumber(fileDiff.misses)
  }
  return (
    <div>
      <ReportLink report={report} />
      <h2 className='subtitle'>
        Filename:{' '}
        <a
          href={
            'https://github.com/' +
            report.organization +
            '/' +
            report.repo +
            '/blob/' +
            report.commit_hash +
            '/' +
            filename
          }
        >
          {filename}
        </a>
      </h2>
      <p>
        Overall file coverage:
        <span className={'tag is-light ' + calcTagClassName(data.line_rate)}>
          {(data.line_rate * 100).toFixed(1)}%
        </span>
        - Diff file coverage:
        <span className={'tag is-light ' + calcTagClassName(report.line_rate)}>
          {diff_file_coverage}
        </span>
        - Covered lines:
        <span className='tag is-primary is-light'>
          {fmtNumber(report.coverage.lines_covered)}
        </span>
        - Total lines:
        <span className='tag is-primary is-light'>
          {fmtNumber(report.coverage.lines_valid)}
        </span>
        - Diff covered lines:
        <span className='tag is-primary is-light'>{diff_covered_lines}</span>-
        Diff missed lines:
        <span className='tag is-primary is-light'>{diff_missed_lines}</span>
      </p>

      <File
        report={report}
        filename={filename}
        fileDiff={fileDiff}
        fileCoverage={data}
      />
    </div>
  )
}

function FilePage ({ params }) {
  const router = useRouter()
  const { filename } = router.query

  const { data, error } = useSWR(
    `${apiUrl}/${params.org}/repos/${params.repo}/pulls/${params.pull}/${params.commit}/report`,
    fetcher
  )
  if (!data) {
    return <div />
  }

  return (
    <Layout title='File: Open Coverage'>
      <div className='container'>
        <div className='section'>
          <FileCoverage report={data} filename={filename} />
        </div>
      </div>
    </Layout>
  )
}

// This also gets called at build time
export async function getServerSideProps ({ params }) {
  // params contains the post `id`.
  // If the route is like /posts/1, then params.id is 1
  //   const res = await fetch(`https://.../posts/${params.id}`)
  //   const post = await res.json()

  // Pass post data to the page via props
  return {
    props: {
      params
    }
  }
}

export default FilePage
