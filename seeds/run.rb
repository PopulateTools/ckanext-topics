require 'http'
require 'yaml'
require 'json'
require 'byebug'

conf = YAML.load_file('config.yml')

API_HOST = conf['api_host']
API_KEY  = conf['api_key']

vocabularies = YAML.load_file('vocabularies.yml')

vocabularies.each do |vocabulary_name, tags|

  # create vocabulary

  puts "\nCreating vocabulary #{vocabulary_name}..."
  puts "----------------------------------------\n"

  response = HTTP.headers('Authorization' => API_KEY)
                 .post("#{API_HOST}/api/action/vocabulary_create", json: { name: vocabulary_name })

  puts "\t=> Response code: #{response.code}"

  vocabulary_id = JSON.parse(response.body)['result']['id']

  # create vocabulary tags

  tags.each do |tag|
    print "\tCreating tag #{tag}... "

    json_body = { name: tag, vocabulary_id: vocabulary_id }

    response = HTTP.headers('Authorization' => API_KEY)
                   .post("#{API_HOST}/api/action/tag_create", json: json_body)

    puts "[#{response.code}]"
  end
end

puts '[END]'