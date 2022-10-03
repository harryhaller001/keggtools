
import { getAssetFromKV } from '@cloudflare/kv-asset-handler'

const DEBUG = false

addEventListener('fetch', event => {
	try {

		// check if request is not simply an http request
		if(event.request.url.indexOf('http://') === -1) {
			event.respondWith(handleEvent(event))
		} else {
			// redirect non http requests to https
			Response.redirect('https' + event.request.url.substring(4, event.request.url.length))
		}


	} catch (e) {
		if (DEBUG) {
			return event.respondWith(
				new Response(e.message || e.toString(), {
					status: 500,
				}),
			)
		} else {
            event.respondWith(new Response('Internal Error', { status: 500 }))
        }
	}
})

async function handleEvent(event) {
	// eslint-disable-next-line no-unused-vars
	const url = new URL(event.request.url)
	let options = {}

	try {
		if (DEBUG) {
			options.cacheControl = {
				bypassCache: true,
			}
		}
		return await getAssetFromKV(event, options)
	} catch (e) {
	/**
	 * Fix vue router paths by redirecting to base directory in case of a 404 => serve index.html
	 * We won't return a 404 status code though as it's part of our normal design
	 */
		return getAssetFromKV(event, {
			mapRequestToAsset: req => new Request(`${new URL(req.url).origin}/index.html`, req),
		})
	}
}
