import assert from 'node:assert/strict'
import test from 'node:test'
import { fetchAPI } from './api.js'

test('API client preserves authenticated requests and returns JSON', async (t) => {
  t.mock.method(globalThis, 'fetch', async (url, options) => {
    assert.ok(url.endsWith('/auth/login'))
    assert.equal(options.credentials, 'include')
    assert.equal(options.method, 'POST')
    assert.equal(options.headers['Content-Type'], 'application/json')
    return new Response(JSON.stringify({ success: true, username: 'tester' }), {
      headers: { 'Content-Type': 'application/json' },
    })
  })
  assert.deepEqual(await fetchAPI('/auth/login', { method: 'POST', credentials: 'include' }), {
    success: true, username: 'tester',
  })
})

test('API client surfaces backend validation errors', async (t) => {
  t.mock.method(console, 'error', () => {})
  t.mock.method(globalThis, 'fetch', async () => new Response(
    JSON.stringify({ error: 'Password must be at least 8 characters' }), {
      status: 400, headers: { 'Content-Type': 'application/json' },
    }))
  await assert.rejects(fetchAPI('/auth/register'), /Password must be at least 8 characters/)
})

test('API client explains non-JSON backend responses', async (t) => {
  t.mock.method(console, 'error', () => {})
  t.mock.method(globalThis, 'fetch', async () => new Response('<!DOCTYPE html>', {
    status: 500, headers: { 'Content-Type': 'text/html' },
  }))
  await assert.rejects(fetchAPI('/auth/me'), /unexpected response.*HTTP 500/)
})
